from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import uuid

class IdentificationResult(BaseModel):
    method: str
    company_name: Optional[str] = None
    confidence: float
    raw_data: Optional[Dict] = None

class VisitorData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ip_address: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Identification Results
    company_name: Optional[str] = None
    confidence_score: float = 0.0
    identification_method: Optional[str] = None
    is_isp: bool = False
    
    # All layer results
    all_results: List[IdentificationResult] = []
    
    # Enrichment Data
    reverse_dns: Optional[str] = None
    asn: Optional[str] = None
    asn_org: Optional[str] = None
    
    # Location Data
    country: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    
    # Network Data
    isp: Optional[str] = None
    org: Optional[str] = None
    
    # Client-Side Data (if available)
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    page_url: Optional[str] = None
    
    # Manual Override
    manual_company: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "ip_address": "8.8.8.8",
                "company_name": "Google LLC",
                "confidence_score": 0.95,
                "country": "United States"
            }
        }

class TrackingRequest(BaseModel):
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    page_url: Optional[str] = None

class AnalyticsSummary(BaseModel):
    total_visitors: int
    identified_visitors: int
    identification_rate: float
    top_companies: List[Dict]
    visitors_by_country: List[Dict]
    recent_visitors: List[VisitorData]