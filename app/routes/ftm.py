from fastapi import APIRouter


router = APIRouter(prefix="/ftm", tags=["Fairway Transfer Messages"])


@router.get("/search")
def search_ftm_messages(query: str):
    return {"message": f"Searching FTM messages with query: {query}"}
