from pydantic import BaseModel
from typing import Optional

class RepoRequest(BaseModel):
    repo_url: str
    # Optional personal access token for cloning private repos. Only used
    # for the clone operation itself - never persisted or logged.
    github_token: Optional[str] = None

class RepoIngestRequest(BaseModel):
    repo_name: str
