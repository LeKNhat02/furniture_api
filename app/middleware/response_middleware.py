from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import json

class ResponseWrapperMiddleware(BaseHTTPMiddleware):
    """Middleware để wrap responses trong format {'data': ...} cho các routes không phải auth"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Bỏ qua nếu là auth routes hoặc static files
        if request.url.path.startswith("/api/auth") or request.url.path.startswith("/uploads"):
            return response
        
        # Chỉ wrap JSON responses
        if isinstance(response, JSONResponse):
            try:
                body = json.loads(response.body.decode())
                
                # Nếu response đã có format chuẩn thì bỏ qua
                if isinstance(body, dict) and ("data" in body or "access_token" in body or "message" in body):
                    return response
                
                # Wrap response trong format {'data': ...}
                # Xử lý cả list và dict
                wrapped_body = {"data": body}
                return JSONResponse(content=wrapped_body, status_code=response.status_code)
            except (json.JSONDecodeError, AttributeError):
                # Nếu không parse được thì trả về nguyên bản
                return response
        
        return response

