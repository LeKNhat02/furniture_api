from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """Base repository class với common database operations"""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Get single record by ID"""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[dict] = None
    ) -> List[ModelType]:
        """Get multiple records with pagination and filters"""
        query = db.query(self.model)
        
        # Apply filters if provided
        if filters:
            filter_conditions = []
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    filter_conditions.append(getattr(self.model, key) == value)
            
            if filter_conditions:
                query = query.filter(and_(*filter_conditions))
        
        return query.offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create new record"""
        if hasattr(obj_in, 'dict'):
            obj_in_data = obj_in.dict()
        else:
            obj_in_data = obj_in
            
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, 
        db: Session, 
        *, 
        db_obj: ModelType, 
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """Update existing record"""
        if hasattr(obj_in, 'dict'):
            update_data = obj_in.dict(exclude_unset=True)
        else:
            update_data = obj_in
            
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, *, id: int) -> Optional[ModelType]:
        """Delete record by ID"""
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj
    
    def soft_delete(self, db: Session, *, id: int) -> Optional[ModelType]:
        """Soft delete by setting is_active = False"""
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj and hasattr(obj, 'is_active'):
            obj.is_active = False
            db.commit()
            db.refresh(obj)
        return obj
    
    def search(
        self, 
        db: Session, 
        *, 
        search_term: str, 
        search_fields: List[str],
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Search records by multiple fields"""
        search_conditions = []
        
        for field in search_fields:
            if hasattr(self.model, field):
                attr = getattr(self.model, field)
                search_conditions.append(attr.ilike(f"%{search_term}%"))
        
        if not search_conditions:
            return []
        
        query = db.query(self.model).filter(or_(*search_conditions))
        return query.offset(skip).limit(limit).all()
    
    def count(self, db: Session, *, filters: Optional[dict] = None) -> int:
        """Count records with optional filters"""
        query = db.query(self.model)
        
        if filters:
            filter_conditions = []
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    filter_conditions.append(getattr(self.model, key) == value)
            
            if filter_conditions:
                query = query.filter(and_(*filter_conditions))
        
        return query.count()