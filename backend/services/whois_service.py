import subprocess
import re
from typing import Optional, Dict

class WhoisService:
    """Layer 1: WHOIS Lookup - Free, catches 30% (large enterprises)"""
    
    # Known ISPs to filter out
    ISP_KEYWORDS = [
        'comcast', 'verizon', 'at&t', 'att', 'charter', 'cox', 'spectrum',
        'centurylink', 'frontier', 'optimum', 'xfinity', 'bt group', 'virgin media',
        'sky broadband', 'talktalk', 'vodafone', 'telefonica', 'telstra', 'optus',
        'rogers', 'bell canada', 't-mobile', 'sprint', 'orange', 'bouygues'
    ]
    
    def __init__(self):
        self.whois_binary = '/app/whois'
    
    def lookup(self, ip_address: str) -> Dict:
        """Perform WHOIS lookup on IP address"""
        try:
            result = subprocess.run(
                [self.whois_binary, ip_address],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return {"success": False, "error": "WHOIS lookup failed"}
            
            whois_data = result.stdout
            return self._parse_whois(whois_data, ip_address)
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "WHOIS timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _parse_whois(self, whois_data: str, ip_address: str) -> Dict:
        """Parse WHOIS output to extract company information"""
        lines = whois_data.split('\n')
        
        org_name = None
        net_name = None
        descr = None
        country = None
        
        for line in lines:
            line = line.strip()
            
            # Extract Organization Name
            if line.startswith('OrgName:') or line.startswith('Organization:'):
                org_name = line.split(':', 1)[1].strip()
            
            # Extract NetName
            elif line.startswith('NetName:'):
                net_name = line.split(':', 1)[1].strip()
            
            # Extract description (RIPE format)
            elif line.startswith('descr:'):
                if not descr:  # Take first description
                    descr = line.split(':', 1)[1].strip()
            
            # Extract country
            elif line.startswith('Country:') or line.startswith('country:'):
                country = line.split(':', 1)[1].strip()
        
        # Determine company name (prefer OrgName, fallback to NetName or descr)
        company_name = org_name or net_name or descr
        
        if not company_name:
            return {
                "success": False,
                "method": "whois",
                "error": "No organization found"
            }
        
        # Check if it's an ISP
        is_isp = self._is_isp(company_name)
        
        # Calculate confidence
        confidence = 0.0
        if not is_isp:
            confidence = 0.9 if org_name else 0.7
        else:
            confidence = 0.3  # Low confidence for ISPs
        
        return {
            "success": True,
            "method": "whois",
            "company_name": company_name,
            "is_isp": is_isp,
            "confidence": confidence,
            "country": country,
            "raw_data": {
                "org_name": org_name,
                "net_name": net_name,
                "descr": descr
            }
        }
    
    def _is_isp(self, company_name: str) -> bool:
        """Check if the company name is a known ISP"""
        company_lower = company_name.lower()
        
        # Check against known ISP keywords
        for isp_keyword in self.ISP_KEYWORDS:
            if isp_keyword in company_lower:
                return True
        
        # Additional heuristics
        if any(word in company_lower for word in ['cable', 'telecom', 'broadband', 'wireless', 'mobile']):
            return True
        
        return False