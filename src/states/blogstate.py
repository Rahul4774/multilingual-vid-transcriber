from pydantic import BaseModel, Field
from typing import List, Dict, Any, TypedDict, Annotated
from src.states.errorstate import ErrorState

class Blog(BaseModel):
    title:str = Field(description="Title of the blog")
    content:str = Field(description="Content of the blog")

class BlogState(TypedDict):
    topic:str = Field(description="Topic of the blog")
    blog:Blog = Field(description="Blog")
    language:str = Field(description="Language of the blog")
    error:ErrorState = Field(default=None,description="Error state")