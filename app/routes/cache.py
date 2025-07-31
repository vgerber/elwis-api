from fastapi import APIRouter


router = APIRouter(prefix="/cache", tags=["Cache"])


@router.get("/")
def get_cache_info():
    return {"message": "Cache information endpoint"}
