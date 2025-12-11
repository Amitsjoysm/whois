# 🔄 Complete Domain ↔ IP Identification Guide

## Part 1: Domain → IP (Forward DNS Lookup)

### Method 1: Using `dig` (Recommended)
```bash
# Basic lookup
dig google.com

# Short answer only
dig +short google.com

# Get IPv4 addresses (A records)
dig A google.com +short

# Get IPv6 addresses (AAAA records)
dig AAAA google.com +short

# Get all DNS records
dig ANY google.com
```

### Method 2: Using `host`
```bash
# Simple lookup
host google.com

# Show only IP addresses
host -t A google.com

# IPv6 addresses
host -t AAAA google.com
```

### Method 3: Using `nslookup`
```bash
nslookup google.com
```

---

## Part 2: IP → Domain (Reverse DNS Lookup)

### Method 1: Using `dig -x` (Recommended)
```bash
# Reverse lookup
dig -x 8.8.8.8

# Short answer only
dig -x 8.8.8.8 +short
```

### Method 2: Using `host`
```bash
host 8.8.8.8
```

### Method 3: Using `nslookup`
```bash
nslookup 8.8.8.8
```

---

## Part 3: Combining Whois + DNS Tools

### Complete Domain Investigation

#### Step 1: Get IP addresses (DNS)
```bash
dig +short google.com
```

#### Step 2: Get registration info (Whois)
```bash
whois google.com
```

#### Step 3: Get IP network info (Whois)
```bash
# Use the IP from step 1
whois 142.250.185.46
```

### Complete IP Investigation

#### Step 1: Get domain name (Reverse DNS)
```bash
dig -x 8.8.8.8 +short
```

#### Step 2: Get IP network info (Whois)
```bash
whois 8.8.8.8
```

#### Step 3: Get domain registration info (Whois)
```bash
# Use domain from step 1
whois dns.google
```

---

## Part 4: Practical Scripts

### Script 1: Domain → Full Info
```bash
#!/bin/bash
DOMAIN=$1

echo "=== DNS Resolution ==="
dig +short A $DOMAIN
echo ""

echo "=== Domain Registration (Whois) ==="
whois $DOMAIN | head -20
echo ""

echo "=== IP Network Info (Whois) ==="
IP=$(dig +short A $DOMAIN | head -1)
if [ ! -z "$IP" ]; then
    whois $IP | head -20
fi
```

### Script 2: IP → Full Info
```bash
#!/bin/bash
IP=$1

echo "=== Reverse DNS ==="
dig -x $IP +short
echo ""

echo "=== IP Network Info (Whois) ==="
whois $IP | head -20
echo ""

echo "=== Domain Registration (Whois) ==="
DOMAIN=$(dig -x $IP +short | sed 's/\.$//')
if [ ! -z "$DOMAIN" ]; then
    whois $DOMAIN | head -20
fi
```

---

## Part 5: Advanced DNS Queries

### Get Nameservers
```bash
dig NS google.com +short
```

### Get Mail Servers (MX)
```bash
dig MX google.com +short
```

### Get TXT Records (SPF, DKIM, etc.)
```bash
dig TXT google.com +short
```

### Get CNAME (Alias)
```bash
dig CNAME www.example.com +short
```

### Trace DNS Resolution Path
```bash
dig +trace google.com
```

### Query Specific DNS Server
```bash
dig @8.8.8.8 google.com
```

---

## Quick Reference Table

| Task | Tool | Command |
|------|------|---------|
| Domain → IP | `dig` | `dig +short google.com` |
| Domain → IPv6 | `dig` | `dig AAAA +short google.com` |
| IP → Domain | `dig` | `dig -x 8.8.8.8 +short` |
| Domain Registration | `whois` | `whois google.com` |
| IP Network Info | `whois` | `whois 8.8.8.8` |
| Nameservers | `dig` | `dig NS google.com +short` |
| Mail Servers | `dig` | `dig MX google.com +short` |
| All DNS Records | `dig` | `dig ANY google.com` |

---

## Summary

**Use:**
- 🔍 **DNS tools** (`dig`, `host`, `nslookup`) for domain↔IP conversion
- 📋 **Whois** for registration and network allocation info
- 🎯 **Combine both** for complete investigation
