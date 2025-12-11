#!/bin/bash
# Complete Domain Investigation Script
# Usage: ./domain_to_info.sh google.com

if [ -z "$1" ]; then
    echo "Usage: $0 <domain>"
    exit 1
fi

DOMAIN=$1

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Complete Domain Investigation: $DOMAIN"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 1. DNS Resolution
echo "🔹 STEP 1: DNS Resolution (Domain → IP)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
IPS=$(dig +short A $DOMAIN)
if [ ! -z "$IPS" ]; then
    echo "IPv4 Addresses:"
    echo "$IPS" | nl
else
    echo "No IPv4 addresses found"
fi
echo ""

IPV6S=$(dig +short AAAA $DOMAIN)
if [ ! -z "$IPV6S" ]; then
    echo "IPv6 Addresses:"
    echo "$IPV6S" | nl
fi
echo ""

# 2. Nameservers
echo "🔹 STEP 2: Nameservers"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
dig +short NS $DOMAIN | nl
echo ""

# 3. Mail Servers
echo "🔹 STEP 3: Mail Servers (MX Records)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
MX=$(dig +short MX $DOMAIN)
if [ ! -z "$MX" ]; then
    echo "$MX" | nl
else
    echo "No MX records found"
fi
echo ""

# 4. Domain Registration (Whois)
echo "🔹 STEP 4: Domain Registration Info (Whois)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
/app/whois $DOMAIN 2>/dev/null | grep -E "(Domain Name|Registrar|Creation Date|Registry Expiry Date|Name Server)" | head -10
echo ""

# 5. IP Network Information
echo "🔹 STEP 5: IP Network Information (First IP)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
FIRST_IP=$(echo "$IPS" | head -1)
if [ ! -z "$FIRST_IP" ]; then
    echo "Checking IP: $FIRST_IP"
    /app/whois $FIRST_IP 2>/dev/null | grep -E "(NetRange|CIDR|NetName|Organization|OrgName|Country)" | head -10
else
    echo "No IP to check"
fi
echo ""

echo "✅ Investigation complete!"
