from pydantic import BaseModel
from datetime import datetime


class MessageOut(BaseModel):
    id: int
    channel_name: str
    text: str
    timestamp: datetime


class CheckpointStatus(BaseModel):
    name_ar: str
    name_en: str
    status: str
    color: str
    last_update: str
    summary: str


class StatusResponse(BaseModel):
    checkpoints: list[CheckpointStatus]
    generated_at: datetime


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources_count: int
