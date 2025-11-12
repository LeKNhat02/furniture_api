from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.database.models import Customer, Sale
from app.schemas.customer_schema import CustomerCreate, CustomerUpdate, CustomerResponse
from fastapi import HTTPException, status

class CustomerService:
    @staticmethod
    def create_customer(db: Session, customer_data: CustomerCreate):
        # Kiểm tra phone đã tồn tại chưa
        if customer_data.phone:
            existing = db.query(Customer).filter(Customer.phone == customer_data.phone).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number already exists"
                )
        
        customer = Customer(**customer_data.dict())
        db.add(customer)
        db.commit()
        db.refresh(customer)
        
        # Return with computed fields for frontend compatibility
        return CustomerService._transform_customer_response(db, customer)
    
    @staticmethod
    def get_all_customers(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: str = ""
    ):
        query = db.query(Customer).filter(Customer.is_active)
        
        if search:
            query = query.filter(
                or_(
                    Customer.name.contains(search),
                    Customer.email.contains(search),
                    Customer.phone.contains(search),
                    Customer.city.contains(search)
                )
            )
        
        customers = query.offset(skip).limit(limit).all()
        
        # Transform all customers to include computed fields
        result = []
        for customer in customers:
            result.append(CustomerService._transform_customer_response(db, customer))
        
        return result
    
    @staticmethod
    def get_customer_by_id(db: Session, customer_id: int):
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        return CustomerService._transform_customer_response(db, customer)
    
    @staticmethod
    def update_customer(
        db: Session,
        customer_id: int,
        customer_data: CustomerUpdate
    ):
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Kiểm tra phone nếu có thay đổi
        if customer_data.phone and customer_data.phone != customer.phone:
            existing = db.query(Customer).filter(
                Customer.phone == customer_data.phone,
                Customer.id != customer_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number already exists"
                )
        
        for key, value in customer_data.dict(exclude_unset=True).items():
            setattr(customer, key, value)
        
        db.commit()
        db.refresh(customer)
        
        return CustomerService._transform_customer_response(db, customer)
    
    @staticmethod
    def delete_customer(db: Session, customer_id: int):
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Soft delete by setting is_active = False
        customer.is_active = False
        db.commit()
        return {"message": "Customer deleted successfully"}
    
    @staticmethod
    def _transform_customer_response(db: Session, customer: Customer) -> CustomerResponse:
        """Transform customer to match frontend expectations with computed fields"""
        
        # Calculate totalSpent and totalOrders from sales
        sales_stats = db.query(
            func.coalesce(func.sum(Sale.final_amount), 0).label('total_spent'),
            func.count(Sale.id).label('total_orders')
        ).filter(
            Sale.customer_id == customer.id,
            Sale.status == 'completed'  # Only count completed sales
        ).first()
        
        return CustomerResponse(
            id=str(customer.id),  # Convert to String for frontend compatibility
            name=customer.name,
            email=customer.email,
            phone=customer.phone,
            address=customer.address,
            city=customer.city,
            country=customer.country,
            notes=customer.notes,
            isActive=customer.is_active,  # camelCase for frontend
            totalSpent=float(sales_stats.total_spent) if sales_stats.total_spent else 0.0,  # camelCase
            totalOrders=int(sales_stats.total_orders) if sales_stats.total_orders else 0,  # camelCase
            createdAt=customer.created_at,  # camelCase
            updatedAt=customer.updated_at   # camelCase
        )

