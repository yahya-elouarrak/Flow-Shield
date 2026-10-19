from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["docs"])

@router.get("/openapi.json", include_in_schema=False)
def get_dummy_openapi():
    """
    Simulates an exposed OpenAPI documentation endpoint.
    """
    return JSONResponse({
        "openapi": "3.0.0",
        "info": {"title": "Internal Admin API", "version": "1.0"},
        "paths": {
            "/admin/reset": {
                "post": {"summary": "Reset database"}
            }
        }
    })
