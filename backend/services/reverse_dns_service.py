import subprocess
import re
from typing import Optional, Dict

class ReverseDNSService:
    """Layer 3: Reverse DNS Intelligence - Free, catches +5%"""
    
    # Cloud/hosting providers to skip
    HOSTING_PROVIDERS = [
        'amazonaws.com', 'googleusercontent.com', 'compute.internal',
        'cloudfront.net', 'azurewebsites.net', 'digitalocean.com',
        'linode.com', 'vultr.com', 'ovh.net'
    ]
    
    def __init__(self):
        pass
    
    def lookup(self, ip_address: str) -> Dict:
        """Perform reverse DNS lookup and extract company info"""
        try:
            # Use dig for reverse DNS
            result = subprocess.run(
                ['dig', '-x', ip_address, '+short'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0 or not result.stdout.strip():
                return {"success": False, "error": "No reverse DNS found"}
            
            hostname = result.stdout.strip().rstrip('.')
            
            if not hostname:
                return {"success": False, "error": "Empty reverse DNS"}
            
            return self._parse_hostname(hostname)
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "DNS timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _parse_hostname(self, hostname: str) -> Dict:
        """Extract company name from hostname"""
        
        # Check if it's a generic hosting provider
        if any(provider in hostname for provider in self.HOSTING_PROVIDERS):
            return {
                "success": False,
                "method": "reverse_dns",
                "error": "Generic hosting provider",
                "hostname": hostname
            }
        
        # Extract domain (remove subdomains)
        domain_match = re.search(r'([a-zA-Z0-9-]+\.[a-zA-Z]{2,})$', hostname)
        if not domain_match:
            return {"success": False, "error": "Could not extract domain"}
        
        domain = domain_match.group(1)
        
        # Extract company name from domain
        # Examples: shopify.com -> Shopify, stripe.com -> Stripe
        company_name = domain.split('.')[0]
        company_name = company_name.replace('-', ' ').title()
        
        # Check if hostname contains corporate patterns
        corporate_patterns = ['vpn', 'office', 'corp', 'gateway', 'corporate', 'hq', 'internal']
        has_corporate_pattern = any(pattern in hostname.lower() for pattern in corporate_patterns)
        
        # Calculate confidence based on patterns
        confidence = 0.7 if has_corporate_pattern else 0.5
        
        return {
            "success": True,
            "method": "reverse_dns",
            "company_name": company_name,
            "confidence": confidence,
            "hostname": hostname,
            "domain": domain,
            "is_corporate": has_corporate_pattern
        }