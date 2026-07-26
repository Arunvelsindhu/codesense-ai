from pydantic import BaseModel

class QueryRequest(BaseModel):
    repo_name: str
    question: str
class CodeSnippetRequest(BaseModel):
    code: str
    language: str = "auto"