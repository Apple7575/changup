from pydantic import BaseModel, Field
from typing import Any, Optional

class ApiResponse(BaseModel):
    success: bool = True
    data: Any
    message: str

class BusinessType(BaseModel):
    business_type_id: str
    name: str
    description: str
    icon: str
    enabled: bool = True

class Region(BaseModel):
    region_id: str
    sido: str
    sigungu: str
    dong: str
    display_name: str
    latitude: float
    longitude: float
    available: bool = True

class AnalyzeRequest(BaseModel):
    business_type_id: str
    region_id: str
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    include_redzone_summary: bool = True

class ReportRequest(BaseModel):
    analysis_id: str
    business_type: dict
    region: dict
    score_summary: dict
    scores: dict
    redzone_summary: dict | None = None
    risk_labels: list[Any] = Field(default_factory=list)

class ChatRequest(BaseModel):
    analysis_id: str
    report_id: Optional[str] = None
    question: str
    analysis_snapshot: Optional[dict] = None

class CompareRequest(BaseModel):
    business_type_id: str
    analysis_ids: list[str] = Field(default_factory=list)
    region_ids: list[str] = Field(default_factory=list)
    use_cache: bool = True
