from pydantic import BaseModel, Field
from typing import TypedDict, Annotated, Any, Optional, Literal
from src.states.errorstate import ErrorState

class VideoState(BaseModel):
    videotitle:str = Field(default="",description="Title of video")
    audiodata:Optional[Any]= Field(
        default=None,
        description="Audio data loaded video object"
    )

class UserInput(BaseModel):
    url:Optional[str]=Field(description="url shared by user input")
    language:str=Field(default="english", description="language shared by user input")

class Articlereview(BaseModel):
    needchanges: Literal["yes","no"] = Field(description="Need changes in article")
    suggestions:str = Field(description="Suggestions for improvement")
    compliance_percentage:float = Field(description="Compliance percentage of article")
    relevance_percentage:float = Field(description="Relevance percentage of article")

class VideoAgentState(TypedDict):
    videoinput:str = Field(description="Video data given by user") ##
    videopath:str = Field(description="File path or URL of Video") ##
    video_data:VideoState ##
    transcript:str = Field(description="Transcript of video") ##
    language:str = Field(description="Language of transcript") ##
    summary:str = Field(description="Summary of video") ##
    finalarticle:str = Field(description="Final article generated from summary and transcript")
    review: Articlereview
    error: ErrorState = Field(default=None,description="Error state")