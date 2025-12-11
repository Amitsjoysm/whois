#!/bin/bash
# Batch Domain/IP Lookup Tool
# Usage: ./batch_lookup.sh domains.txt
# Or: echo "google.com" | ./batch_lookup.sh

INPUT_FILE=${1:--}

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          Batch Domain/IP Lookup Tool                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Function to detect if input is IP or domain
is_ip() {
    if [[ $1 =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Process each line
while IFS= read -r line; do
    # Skip empty lines and comments
    [[ -z "$line" || "$line" =~ ^# ]] && continue
    
    # Remove whitespace
    line=$(echo "$line" | xargs)
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔍 Analyzing: $line"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if is_ip "$line"; then
        # It's an IP address
        echo "Type: IP Address"
        echo ""
        
        # Reverse DNS
        echo "📍 Reverse DNS:"
        DOMAIN=$(dig -x $line +short 2>/dev/null)
        if [ ! -z "$DOMAIN" ]; then
            echo "  → $DOMAIN"
        else
            echo "  → No reverse DNS"
        fi
        echo ""
        
        # IP Network Info
        echo "🌐 Network Info:"
        /app/whois $line 2>/dev/null | grep -E "(NetRange|CIDR|OrgName|NetName|Organization|Country)" | head -5 | sed 's/^/  /'
        
    else
        # It's a domain
        echo "Type: Domain Name"
        echo ""
        
        # DNS Resolution
        echo "📍 IP Addresses:"
        IPS=$(dig +short A $line 2>/dev/null)
        if [ ! -z "$IPS" ]; then
            echo "$IPS" | sed 's/^/  → /'
        else
            echo "  → No A records found"
        fi
        echo ""
        
        # Registration Info
        echo "📋 Registration:"
        /app/whois $line 2>/dev/null | grep -E "(Domain Name|Registrar:|Creation Date|Registry Expiry Date)" | head -4 | sed 's/^/  /'
        
        # Network info for first IP
        FIRST_IP=$(echo "$IPS" | head -1)
        if [ ! -z "$FIRST_IP" ]; then
            echo ""
            echo "🌐 Network (First IP: $FIRST_IP):"
            /app/whois $FIRST_IP 2>/dev/null | grep -E "(OrgName|NetName|Organization|Country)" | head -3 | sed 's/^/  /'
        fi
    fi
    
    echo ""
    
done < "$INPUT_FILE"

echo "✅ Batch lookup complete!"
