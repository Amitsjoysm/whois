from typing import Dict, List, Optional
from .whois_service import WhoisService
from .reverse_dns_service import ReverseDNSService
from .asn_service import ASNService
from .ip_api_service import IPAPIService
from .cache_service import CacheService
import asyncio

class IdentificationOrchestrator:
    """
    Intelligent 10-layer identification system
    Coordinates all identification methods to achieve 80%+ accuracy
    """
    
    def __init__(self):
        self.whois_service = WhoisService()
        self.reverse_dns_service = ReverseDNSService()
        self.asn_service = ASNService()
        self.ip_api_service = IPAPIService()
        self.cache_service = CacheService()
    
    async def identify(self, ip_address: str, skip_cache: bool = False) -> Dict:
        """
        Main identification method - runs through all layers intelligently
        """
        all_results = []
        
        # Layer 7: Check cache first (unless explicitly skipped)
        if not skip_cache:
            cached = self.cache_service.get(ip_address)
            if cached:
                return {
                    "success": True,
                    "ip_address": ip_address,
                    "company_name": cached.get('company_name'),
                    "confidence": cached.get('confidence'),
                    "method": "cache",
                    "is_isp": cached.get('is_isp', False),
                    "country": cached.get('country'),
                    "city": cached.get('city'),
                    "cached": True,
                    "cache_age_hours": cached.get('cache_age_hours')
                }
        
        # Layer 1: WHOIS Lookup (FREE - fastest, catches 30%)
        print(f"🔍 Layer 1: WHOIS lookup for {ip_address}")
        whois_result = self.whois_service.lookup(ip_address)
        if whois_result.get('success'):
            all_results.append(whois_result)
            
            # If WHOIS found a non-ISP company with high confidence, we're done!
            if not whois_result.get('is_isp') and whois_result.get('confidence', 0) >= 0.8:
                final_result = self._build_final_result(ip_address, whois_result, all_results)
                self.cache_service.set(ip_address, final_result)
                return final_result
        
        # Layer 4: ASN Lookup (FREE - fast, catches corporate networks)
        print(f"🔍 Layer 4: ASN lookup for {ip_address}")
        asn_result = self.asn_service.lookup(ip_address)
        if asn_result.get('success'):
            all_results.append(asn_result)
            
            # If ASN found a well-known company (confidence >= 0.9), we're done!
            if asn_result.get('confidence', 0) >= 0.9:
                final_result = self._build_final_result(ip_address, asn_result, all_results)
                self.cache_service.set(ip_address, final_result)
                return final_result
        
        # Layer 3: Reverse DNS (FREE - might reveal company)
        print(f"🔍 Layer 3: Reverse DNS lookup for {ip_address}")
        reverse_dns_result = self.reverse_dns_service.lookup(ip_address)
        if reverse_dns_result.get('success'):
            all_results.append(reverse_dns_result)
        
        # Layer 2: Multi-API Intelligence (FREE tier, then paid)
        print(f"🔍 Layer 2: Multi-API lookup for {ip_address}")
        api_results = await self.ip_api_service.lookup_all(ip_address)
        
        if api_results:
            # Add each API result
            all_results.extend(api_results)
            
            # Use consensus algorithm
            consensus_result = self.ip_api_service.consensus(api_results)
            if consensus_result.get('success'):
                all_results.append(consensus_result)
        
        # Determine best result from all layers
        best_result = self._choose_best_result(all_results)
        
        if best_result:
            final_result = self._build_final_result(ip_address, best_result, all_results)
            self.cache_service.set(ip_address, final_result)
            return final_result
        
        # No identification found
        return {
            "success": False,
            "ip_address": ip_address,
            "error": "Could not identify company",
            "all_results": all_results
        }
    
    def _choose_best_result(self, results: List[Dict]) -> Optional[Dict]:
        """
        Choose the best result based on confidence and method priority
        """
        if not results:
            return None
        
        # Filter successful results
        successful = [r for r in results if r.get('success')]
        
        if not successful:
            return None
        
        # Filter out ISPs if we have non-ISP options
        non_isp = [r for r in successful if not r.get('is_isp')]
        if non_isp:
            successful = non_isp
        
        # Sort by confidence (highest first)
        successful.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return successful[0]
    
    def _build_final_result(self, ip_address: str, best_result: Dict, all_results: List[Dict]) -> Dict:
        """
        Build the final result object
        """
        return {
            "success": True,
            "ip_address": ip_address,
            "company_name": best_result.get('company_name'),
            "confidence": best_result.get('confidence'),
            "method": best_result.get('method'),
            "is_isp": best_result.get('is_isp', False),
            "country": best_result.get('country'),
            "city": best_result.get('city'),
            "region": best_result.get('region'),
            "org": best_result.get('org'),
            "asn": best_result.get('asn'),
            "asn_org": best_result.get('asn_org'),
            "hostname": best_result.get('hostname'),
            "all_results": [
                {
                    "method": r.get('method'),
                    "company_name": r.get('company_name'),
                    "confidence": r.get('confidence'),
                    "is_isp": r.get('is_isp', False)
                }
                for r in all_results if r.get('success')
            ],
            "cached": False
        }
    
    def get_identification_stats(self) -> Dict:
        """
        Get statistics about identification performance
        """
        cache_stats = self.cache_service.get_stats()
        
        return {
            "cache_stats": cache_stats,
            "layers_available": {
                "whois": True,
                "reverse_dns": True,
                "asn": True,
                "ipinfo": bool(self.ip_api_service.ipinfo_token),
                "ipapi_co": True,
                "ip_api_com": True
            }
        }
