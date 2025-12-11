from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from typing import Optional, Dict

class CacheService:
    """Layer 7: Smart Caching - Reduces API costs by 50%+"""
    
    def __init__(self):
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017/')
        db_name = os.getenv('DATABASE_NAME', 'visitor_tracker')
        
        self.client = MongoClient(mongo_url)
        self.db = self.client[db_name]
        self.cache_collection = self.db['ip_cache']
        self.ttl_days = int(os.getenv('CACHE_TTL_DAYS', '30'))
        
        # Create index for faster lookups
        self.cache_collection.create_index('ip_address')
        self.cache_collection.create_index('timestamp')
    
    def get(self, ip_address: str) -> Optional[Dict]:
        """Get cached result for IP address"""
        result = self.cache_collection.find_one({'ip_address': ip_address})
        
        if not result:
            return None
        
        # Check if cache is expired
        cache_age = datetime.utcnow() - result['timestamp']
        if cache_age > timedelta(days=self.ttl_days):
            # Cache expired, delete it
            self.cache_collection.delete_one({'ip_address': ip_address})
            return None
        
        return {
            'company_name': result.get('company_name'),
            'confidence': result.get('confidence', 0.0),
            'method': result.get('method', 'cache'),
            'is_isp': result.get('is_isp', False),
            'country': result.get('country'),
            'city': result.get('city'),
            'cached': True,
            'cache_age_hours': int(cache_age.total_seconds() / 3600)
        }
    
    def set(self, ip_address: str, data: Dict):
        """Cache result for IP address"""
        cache_entry = {
            'ip_address': ip_address,
            'company_name': data.get('company_name'),
            'confidence': data.get('confidence', 0.0),
            'method': data.get('method'),
            'is_isp': data.get('is_isp', False),
            'country': data.get('country'),
            'city': data.get('city'),
            'timestamp': datetime.utcnow()
        }
        
        # Upsert (update if exists, insert if not)
        self.cache_collection.update_one(
            {'ip_address': ip_address},
            {'$set': cache_entry},
            upsert=True
        )
    
    def clear_old_entries(self):
        """Clear cache entries older than TTL"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.ttl_days)
        result = self.cache_collection.delete_many({'timestamp': {'$lt': cutoff_date}})
        return result.deleted_count
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total = self.cache_collection.count_documents({})
        
        # Count by method
        pipeline = [
            {'$group': {'_id': '$method', 'count': {'$sum': 1}}}
        ]
        by_method = list(self.cache_collection.aggregate(pipeline))
        
        return {
            'total_cached_ips': total,
            'by_method': by_method,
            'ttl_days': self.ttl_days
        }