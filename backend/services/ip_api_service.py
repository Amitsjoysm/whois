import httpx
import os
from typing import Optional, Dict, List
import asyncio

class IPAPIService:
    """Layer 2: Multi-API Intelligence - Free/Paid, catches +20-25%"""
    
    def __init__(self):
        self.ipinfo_token = os.getenv('IPINFO_TOKEN', '')
        self.ipapi_key = os.getenv('IPAPI_KEY', '')
        self.timeout = 5
    
    async def lookup_all(self, ip_address: str) -> List[Dict]:
        """Query all available APIs in parallel"""
        tasks = [
            self.lookup_ipinfo(ip_address),
            self.lookup_ipapi_co(ip_address),
            self.lookup_ip_api_com(ip_address)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and failed lookups
        valid_results = []
        for result in results:
            if isinstance(result, dict) and result.get('success'):
                valid_results.append(result)
        
        return valid_results
    
    async def lookup_ipinfo(self, ip_address: str) -> Dict:
        """Query IPinfo.io API (50k/month free)"""
        try:
            url = f'https://ipinfo.io/{ip_address}/json'
            if self.ipinfo_token:
                url += f'?token={self.ipinfo_token}'
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                if response.status_code != 200:
                    return {"success": False, "error": f"IPinfo API error: {response.status_code}"}
                
                data = response.json()
                
                # Extract company from org field
                org = data.get('org', '')
                company_name = self._extract_company_from_org(org)
                
                return {
                    "success": bool(company_name),
                    "method": "ipinfo",
                    "company_name": company_name,
                    "confidence": 0.8 if company_name else 0.0,
                    "country": data.get('country'),
                    "city": data.get('city'),
                    "region": data.get('region'),
                    "org": org
                }
        except Exception as e:
            return {"success": False, "error": f"IPinfo error: {str(e)}"}
    
    async def lookup_ipapi_co(self, ip_address: str) -> Dict:
        """Query ipapi.co API (30k/month free)"""
        try:
            url = f'https://ipapi.co/{ip_address}/json/'
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                if response.status_code != 200:
                    return {"success": False, "error": f"ipapi.co error: {response.status_code}"}
                
                data = response.json()
                
                # Check for error in response
                if data.get('error'):
                    return {"success": False, "error": data.get('reason', 'Unknown error')}
                
                company_name = data.get('org') or data.get('asn_org')
                if company_name:
                    company_name = self._extract_company_from_org(company_name)
                
                return {
                    "success": bool(company_name),
                    "method": "ipapi_co",
                    "company_name": company_name,
                    "confidence": 0.75 if company_name else 0.0,
                    "country": data.get('country_name'),
                    "city": data.get('city'),
                    "region": data.get('region'),
                    "org": data.get('org')
                }
        except Exception as e:
            return {"success": False, "error": f"ipapi.co error: {str(e)}"}
    
    async def lookup_ip_api_com(self, ip_address: str) -> Dict:
        """Query ip-api.com API (free, 45/min limit)"""
        try:
            url = f'http://ip-api.com/json/{ip_address}?fields=status,message,country,city,regionName,isp,org,as'
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                if response.status_code != 200:
                    return {"success": False, "error": f"ip-api.com error: {response.status_code}"}
                
                data = response.json()
                
                if data.get('status') != 'success':
                    return {"success": False, "error": data.get('message', 'Unknown error')}
                
                # Prefer org over isp
                company_name = data.get('org') or data.get('isp')
                if company_name:
                    company_name = self._extract_company_from_org(company_name)
                
                return {
                    "success": bool(company_name),
                    "method": "ip_api_com",
                    "company_name": company_name,
                    "confidence": 0.7 if company_name else 0.0,
                    "country": data.get('country'),
                    "city": data.get('city'),
                    "region": data.get('regionName'),
                    "org": data.get('org'),
                    "isp": data.get('isp')
                }
        except Exception as e:
            return {"success": False, "error": f"ip-api.com error: {str(e)}"}
    
    def _extract_company_from_org(self, org: str) -> Optional[str]:
        """Extract clean company name from org field"""
        if not org:
            return None
        
        # Remove ASN prefix (e.g., "AS15169 Google LLC" -> "Google LLC")
        org = org.split(' ', 1)[-1] if org.startswith('AS') else org
        
        # Clean up common suffixes
        for suffix in [', Inc.', ' Inc.', ' LLC', ' Ltd.', ' Corporation', ' Corp.', ' Co.']:
            if org.endswith(suffix):
                org = org[:-len(suffix)]
        
        return org.strip() if org else None
    
    def consensus(self, results: List[Dict]) -> Dict:
        """Use consensus algorithm to determine best result"""
        if not results:
            return {"success": False, "error": "No results to analyze"}
        
        # Count company name occurrences
        company_votes = {}
        confidence_scores = {}
        
        for result in results:
            company = result.get('company_name')
            if company:
                company_lower = company.lower()
                company_votes[company_lower] = company_votes.get(company_lower, 0) + 1
                
                # Store highest confidence for this company
                if company_lower not in confidence_scores or result['confidence'] > confidence_scores[company_lower]:
                    confidence_scores[company_lower] = result['confidence']
        
        if not company_votes:
            return {"success": False, "error": "No company names found in results"}
        
        # Find company with most votes
        best_company = max(company_votes.items(), key=lambda x: x[1])
        company_name = best_company[0].title()
        vote_count = best_company[1]
        
        # Calculate consensus confidence
        base_confidence = confidence_scores[best_company[0]]
        consensus_boost = 0.1 * (vote_count - 1)  # Boost confidence if multiple APIs agree
        final_confidence = min(base_confidence + consensus_boost, 0.95)
        
        return {
            "success": True,
            "method": "multi_api_consensus",
            "company_name": company_name,
            "confidence": final_confidence,
            "vote_count": vote_count,
            "total_apis": len(results)
        }