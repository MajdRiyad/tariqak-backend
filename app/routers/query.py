from fastapi import APIRouter
from app.llm.analyzer import answer_query
from app.models import QueryRequest, QueryResponse

router = APIRouter()


@router.post("/", response_model=QueryResponse)
async def post_query(request: QueryRequest):
    """Ask the AI about a specific road or checkpoint."""
    answer, sources_count = await answer_query(request.question)
    return QueryResponse(answer=answer, sources_count=sources_count)
