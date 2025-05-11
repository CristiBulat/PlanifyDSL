from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Request models
class DSLCodeRequest(BaseModel):
    code: str = Field(..., description="DSL code to parse")
    title: Optional[str] = Field(None, description="Title of the floor plan")
    description: Optional[str] = Field(None, description="Description of the floor plan")
    user_id: Optional[int] = Field(None, description="ID of the user creating the floor plan")


# Response models for individual elements
class FloorPlanElement(BaseModel):
    id: str
    type: str
    position: Optional[List[float]] = None
    size: Optional[List[float]] = None
    start: Optional[List[float]] = None
    end: Optional[List[float]] = None
    width: Optional[float] = None
    height: Optional[float] = None
    wall: Optional[str] = None
    direction: Optional[str] = None


# Response model for the complete floor plan
class FloorPlanResponse(BaseModel):
    elements: List[FloorPlanElement]
    svg_url: Optional[str] = None