import subprocess
import re
from typing import Optional, Dict

class ASNService:
    """Layer 4: ASN Intelligence - Free, catches +3%"""
    
    # Well-known corporate ASNs
    CORPORATE_ASNS = {
        'AS714': 'Apple Inc.',
        'AS8075': 'Microsoft Corporation',
        'AS15169': 'Google LLC',
        'AS32934': 'Facebook/Meta',
        'AS2906': 'Netflix',
        'AS16509': 'Amazon.com (AWS)',
        'AS13335': 'Cloudflare',
        'AS20940': 'Akamai',
        'AS36459': 'GitHub',
        'AS54113': 'Fastly',
        'AS46489': 'Twitch',
        'AS16625': 'Akamai Technologies',
        'AS22222': 'Vercel',
    }
    
    def __init__(self):
        pass
    
    def lookup(self, ip_address: str) -> Dict:
        """Lookup ASN for IP address using Team Cymru's service"""
        try:
            # Use whois to query Team Cymru ASN database
            result = subprocess.run(
                ['whois', '-h', 'whois.cymru.com', f' -v {ip_address}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return {"success": False, "error": "ASN lookup failed"}
            
            output = result.stdout
            return self._parse_asn(output)
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "ASN timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _parse_asn(self, output: str) -> Dict:
        """Parse ASN information from whois output"""
        
        lines = output.split('\n')
        asn = None
        asn_org = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Format: AS | IP | BGP Prefix | CC | Registry | Allocated | AS Name
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 7:
                asn = parts[0]
                asn_org = parts[6]
                break
        
        if not asn:
            return {"success": False, "error": "Could not extract ASN"}
        
        # Check if it's a known corporate ASN
        asn_key = f'AS{asn}'
        if asn_key in self.CORPORATE_ASNS:
            return {
                "success": True,
                "method": "asn",
                "company_name": self.CORPORATE_ASNS[asn_key],
                "confidence": 0.95,
                "asn": asn,
                "asn_org": asn_org
            }
        
        # Return ASN org if available
        if asn_org:
            return {
                "success": True,
                "method": "asn",
                "company_name": asn_org,
                "confidence": 0.6,
                "asn": asn,
                "asn_org": asn_org
            }
        
        return {
            "success": False,
            "error": "ASN found but no organization data",
            "asn": asn
        }