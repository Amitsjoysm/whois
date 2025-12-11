from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from typing import Optional, List
import asyncio

from models.visitor import VisitorData, TrackingRequest, AnalyticsSummary
from services.identification_orchestrator import IdentificationOrchestrator

# Load environment variables
load_dotenv()

app = FastAPI(title="Website Traffic Company Revealer API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'visitor_tracker')

client = MongoClient(MONGO_URL)
db = client[DATABASE_NAME]
visitors_collection = db['visitors']

# Create indexes
visitors_collection.create_index('ip_address')
visitors_collection.create_index('timestamp')
visitors_collection.create_index('company_name')

# Initialize identification orchestrator
orchestrator = IdentificationOrchestrator()

@app.get("/")
async def root():
    return {
        "message": "Website Traffic Company Revealer API",
        "version": "1.0.0",
        "endpoints": {
            "track": "/api/track",
            "identify": "/api/identify/{ip}",
            "visitors": "/api/visitors",
            "analytics": "/api/analytics",
            "stats": "/api/stats"
        }
    }

@app.post("/api/track")
async def track_visitor(request: Request, tracking_data: Optional[TrackingRequest] = None):
    """
    Main endpoint for tracking website visitors
    Automatically identifies company from IP address
    """
    try:
        # Get IP from request or tracking data
        if tracking_data and tracking_data.ip_address:
            ip_address = tracking_data.ip_address
        else:
            # Get from request headers (real client IP)
            ip_address = request.client.host
            
            # Check for forwarded IP (if behind proxy)
            forwarded = request.headers.get('X-Forwarded-For')
            if forwarded:
                ip_address = forwarded.split(',')[0].strip()
        
        # Identify company using orchestrator
        identification = await orchestrator.identify(ip_address)
        
        # Create visitor record
        visitor = VisitorData(
            ip_address=ip_address,
            company_name=identification.get('company_name'),
            confidence_score=identification.get('confidence', 0.0),
            identification_method=identification.get('method'),
            is_isp=identification.get('is_isp', False),
            reverse_dns=identification.get('hostname'),
            asn=identification.get('asn'),
            asn_org=identification.get('asn_org'),
            country=identification.get('country'),
            city=identification.get('city'),
            region=identification.get('region'),
            org=identification.get('org'),
            user_agent=tracking_data.user_agent if tracking_data else None,
            referrer=tracking_data.referrer if tracking_data else None,
            page_url=tracking_data.page_url if tracking_data else None,
            all_results=identification.get('all_results', [])
        )
        
        # Save to database
        visitor_dict = visitor.dict()
        visitors_collection.insert_one(visitor_dict)
        
        return {
            "success": True,
            "visitor_id": visitor.id,
            "company_name": visitor.company_name,
            "confidence": visitor.confidence_score,
            "is_isp": visitor.is_isp,
            "cached": identification.get('cached', False)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/identify/{ip_address}")
async def identify_ip(ip_address: str, skip_cache: bool = False):
    """
    Manually identify a single IP address
    Useful for testing and manual lookups
    """
    try:
        result = await orchestrator.identify(ip_address, skip_cache=skip_cache)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/visitors")
async def get_visitors(
    limit: int = 50,
    skip: int = 0,
    company: Optional[str] = None,
    country: Optional[str] = None,
    hide_isp: bool = False
):
    """
    Get list of tracked visitors with filtering
    """
    try:
        # Build query
        query = {}
        if company:
            query['company_name'] = {'$regex': company, '$options': 'i'}
        if country:
            query['country'] = country
        if hide_isp:
            query['is_isp'] = False
        
        # Get visitors
        visitors = list(
            visitors_collection
            .find(query)
            .sort('timestamp', -1)
            .skip(skip)
            .limit(limit)
        )
        
        # Convert ObjectId to string
        for visitor in visitors:
            visitor['_id'] = str(visitor['_id'])
        
        total = visitors_collection.count_documents(query)
        
        return {
            "visitors": visitors,
            "total": total,
            "limit": limit,
            "skip": skip
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics")
async def get_analytics(days: int = 7):
    """
    Get analytics summary for dashboard
    """
    try:
        # Date range
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Total visitors
        total_visitors = visitors_collection.count_documents({
            'timestamp': {'$gte': cutoff_date}
        })
        
        # Identified visitors (non-ISP, non-null company)
        identified_visitors = visitors_collection.count_documents({
            'timestamp': {'$gte': cutoff_date},
            'company_name': {'$ne': None},
            'is_isp': False
        })
        
        # Identification rate
        identification_rate = (identified_visitors / total_visitors * 100) if total_visitors > 0 else 0
        
        # Top companies
        pipeline = [
            {'$match': {
                'timestamp': {'$gte': cutoff_date},
                'company_name': {'$ne': None},
                'is_isp': False
            }},
            {'$group': {
                '_id': '$company_name',
                'count': {'$sum': 1},
                'avg_confidence': {'$avg': '$confidence_score'}
            }},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]
        top_companies = list(visitors_collection.aggregate(pipeline))
        
        # Visitors by country
        pipeline = [
            {'$match': {
                'timestamp': {'$gte': cutoff_date},
                'country': {'$ne': None}
            }},
            {'$group': {
                '_id': '$country',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]
        visitors_by_country = list(visitors_collection.aggregate(pipeline))
        
        # Recent visitors
        recent_visitors = list(
            visitors_collection
            .find({'timestamp': {'$gte': cutoff_date}})
            .sort('timestamp', -1)
            .limit(20)
        )
        
        # Convert ObjectId to string
        for visitor in recent_visitors:
            visitor['_id'] = str(visitor['_id'])
        
        return {
            "total_visitors": total_visitors,
            "identified_visitors": identified_visitors,
            "identification_rate": round(identification_rate, 2),
            "top_companies": [
                {
                    "company": item['_id'],
                    "count": item['count'],
                    "avg_confidence": round(item['avg_confidence'], 2)
                }
                for item in top_companies
            ],
            "visitors_by_country": [
                {"country": item['_id'], "count": item['count']}
                for item in visitors_by_country
            ],
            "recent_visitors": recent_visitors,
            "period_days": days
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    """
    Get system statistics (cache stats, layer availability)
    """
    try:
        stats = orchestrator.get_identification_stats()
        
        # Add database stats
        total_visitors = visitors_collection.count_documents({})
        stats['database'] = {
            'total_visitors': total_visitors
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/visitors/{visitor_id}")
async def delete_visitor(visitor_id: str):
    """
    Delete a visitor record
    """
    try:
        from bson import ObjectId
        result = visitors_collection.delete_one({'_id': ObjectId(visitor_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Visitor not found")
        
        return {"success": True, "message": "Visitor deleted"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/visitors/{visitor_id}/company")
async def update_visitor_company(visitor_id: str, company_name: str):
    """
    Manually correct company name for a visitor
    This helps improve the learning database
    """
    try:
        from bson import ObjectId
        result = visitors_collection.update_one(
            {'_id': ObjectId(visitor_id)},
            {'$set': {'manual_company': company_name}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Visitor not found")
        
        return {"success": True, "message": "Company updated"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
