#!/bin/bash
# Complete IP Investigation Script
# Usage: ./ip_to_info.sh 8.8.8.8

if [ -z "$1" ]; then
    echo "Usage: $0 <ip_address>"
    exit 1
fi

IP=$1

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Complete IP Investigation: $IP"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 1. Reverse DNS Lookup
echo "🔹 STEP 1: Reverse DNS (IP → Domain)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
DOMAINS=$(dig -x $IP +short)
if [ ! -z "$DOMAINS" ]; then
    echo "Reverse DNS results:"
    echo "$DOMAINS" | nl
    MAIN_DOMAIN=$(echo "$DOMAINS" | head -1 | sed 's/\.$//')
else
    echo "No reverse DNS found"
    MAIN_DOMAIN=""
fi
echo ""

# 2. IP Network Information (Whois)
echo "🔹 STEP 2: IP Network Allocation (Whois)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
/app/whois $IP 2>/dev/null | grep -E "(NetRange|CIDR|NetName|NetHandle|Organization|OrgName|Address|City|Country|inetnum|netname|descr|country)" | head -15
echo ""

# 3. Domain Registration (if reverse DNS found)
if [ ! -z "$MAIN_DOMAIN" ]; then
    echo "🔹 STEP 3: Domain Registration Info (Whois)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Checking domain: $MAIN_DOMAIN"
    /app/whois $MAIN_DOMAIN 2>/dev/null | grep -E "(Domain Name|Registrar|Creation Date|Registry Expiry Date|Name Server)" | head -10
    echo ""
    
    # 4. Forward DNS (Domain → IP)
    echo "🔹 STEP 4: Forward DNS Check (Domain → IP)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    FORWARD_IPS=$(dig +short A $MAIN_DOMAIN)
    if [ ! -z "$FORWARD_IPS" ]; then
        echo "IP addresses for $MAIN_DOMAIN:"
        echo "$FORWARD_IPS" | nl
        
        # Check if our IP is in the list
        if echo "$FORWARD_IPS" | grep -q "^$IP$"; then
            echo "✅ Forward DNS matches! $MAIN_DOMAIN → $IP"
        else
            echo "⚠️  Forward DNS doesn't include $IP"
        fi
    else
        echo "No forward DNS found"
    fi
    echo ""
fi

echo "✅ Investigation complete!"
