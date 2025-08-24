from pydantic import BaseModel, Field, RootModel
from typing import Optional, List, Dict, Any, Union
from enum import Enum

class Metadata(BaseModel):
    Summary: List[str] = Field(default_factory=list, description="Summary of the document")
    Title :str
    Author : str
    DateCreated : str
    LastDateModified : str
    Published : str
    Language : str
    PageCount : Union[int, str]
    SentimentTone : str

class ChangeFormat(BaseModel):
    page: str
    changes: str 

class SummaryResponse(RootModel[List[ChangeFormat]]):
    pass

class PromptType(str, Enum):
    DOCUMENT_ANALYSIS = "document_comparison",
    DOCUMENT_COMPARISON = "document_analysis",
    CONTEXTUALIZE_QUESTION = "contextualize_question",
    CONTEXT_QA = "context_qa"
