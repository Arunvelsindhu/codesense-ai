from pydantic import BaseModel
from typing import List

class ChunkMetadata(BaseModel):
    file: str
    type: str
    name: str
    start_line: int
    end_line: int

class QueryResponse(BaseModel):
    answer: str
    sources: List[ChunkMetadata]