from pydantic import BaseModel, Field

class bloggenerationRequest(BaseModel):
    topic: str = Field(description="Topic of the blog")
    language: str = Field(default="English",description="Language of the blog")

class videotranscriptRequest(BaseModel):
    user_input: str = Field(description="user prompt for video to text")