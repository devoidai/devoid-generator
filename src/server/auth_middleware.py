from fastapi import Request
from starlette.responses import JSONResponse

class AuthMiddleware:
    services: list
        
    def __init__(self, services):
        self.services = services
        
    async def __call__(self, request: Request, call_next):
        '''Verifies the token in the request header'''
        if request.url.path.startswith('/img/') or request.url.path.startswith('/favicon.ico'):
            response = await call_next(request)
            return response
        try:
            service = request.headers["service"]
            token = request.headers["authorization"]
            if service in self.services:
                if self.services[service] == token:
                    response = await call_next(request)
                    return response
            return JSONResponse(content='Invalid Authorization', status_code=401)
        except KeyError as er:
            return JSONResponse(content='Invalid Authorization', status_code=401)