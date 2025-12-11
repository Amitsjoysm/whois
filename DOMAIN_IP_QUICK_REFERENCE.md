# 🚀 Domain ↔ IP Quick Reference Card

## ✅ YES - Whois CAN Do This:

| Task | Command | What You Get |
|------|---------|--------------|
| Domain registration info | `./whois google.com` | Registrar, dates, nameservers |
| IP network allocation | `./whois 8.8.8.8` | Organization, network range, location |
| AS number info | `./whois AS15169` | AS owner, registration |
| IP block owner | `./whois 74.125.0.0/16` | Network allocation details |

## ❌ NO - Whois CANNOT Do This:

| Task | ❌ Wrong Tool | ✅ Right Tool | Command |
|------|-------------|--------------|---------|
| Domain → IP | `whois` | `dig` | `dig +short google.com` |
| IP → Domain | `whois` | `dig -x` | `dig -x 8.8.8.8 +short` |
| Live DNS lookup | `whois` | `dig`/`host` | `dig A google.com` |
| Nameserver IPs | `whois` | `dig` | `dig NS google.com +short` |

---

## 📖 Complete Workflows

### Workflow 1: Investigate a Domain
```bash
# 1. Get IP addresses (DNS)
dig +short google.com

# 2. Get nameservers (DNS)
dig NS google.com +short

# 3. Get domain registration (Whois)
./whois google.com

# 4. Get IP network info (Whois) - use IP from step 1
./whois 74.125.126.101

# OR use the automated script:
./domain_to_info.sh google.com
```

### Workflow 2: Investigate an IP
```bash
# 1. Get domain name (Reverse DNS)
dig -x 8.8.8.8 +short

# 2. Get IP network allocation (Whois)
./whois 8.8.8.8

# 3. Get domain registration (Whois) - use domain from step 1
./whois dns.google

# 4. Verify forward lookup (DNS)
dig +short dns.google

# OR use the automated script:
./ip_to_info.sh 8.8.8.8
```

---

## 🔧 Essential Commands

### Domain → IP (DNS Resolution)
```bash
# IPv4 only
dig +short A google.com
dig +short google.com

# IPv6 only
dig +short AAAA google.com

# Using host command
host google.com

# Using nslookup
nslookup google.com
```

### IP → Domain (Reverse DNS)
```bash
# Using dig (recommended)
dig -x 8.8.8.8 +short

# Using host
host 8.8.8.8

# Using nslookup
nslookup 8.8.8.8
```

### Get Other DNS Records
```bash
# Nameservers
dig NS google.com +short

# Mail servers
dig MX google.com +short

# TXT records (SPF, DKIM, etc.)
dig TXT google.com +short

# All records
dig ANY google.com
```

### Get Registration/Network Info
```bash
# Domain registration
./whois google.com

# IP network allocation
./whois 8.8.8.8

# AS number info
./whois AS15169
```

---

## 🎯 One-Liners

### Domain → All IPs
```bash
dig +short google.com
```

### IP → Domain Name
```bash
dig -x 8.8.8.8 +short
```

### Domain → IP → Network Owner
```bash
IP=$(dig +short google.com | head -1) && ./whois $IP | grep -E "(OrgName|NetName)"
```

### IP → Domain → Registration
```bash
DOMAIN=$(dig -x 8.8.8.8 +short | sed 's/\.$//') && ./whois $DOMAIN | grep -E "(Domain Name|Registrar)"
```

---

## 🛠️ Automated Investigation Scripts

### Available Scripts:
- **`./domain_to_info.sh <domain>`** - Complete domain investigation
- **`./ip_to_info.sh <ip>`** - Complete IP investigation

### Examples:
```bash
# Investigate a domain
./domain_to_info.sh github.com

# Investigate an IP
./ip_to_info.sh 1.1.1.1

# Investigate multiple domains
for domain in google.com facebook.com twitter.com; do
    echo "=== $domain ===" 
    ./domain_to_info.sh $domain
    echo ""
done

# Investigate IP range (first IP only)
for i in {1..5}; do
    ./ip_to_info.sh 8.8.8.$i
done
```

---

## 💡 Pro Tips

### Tip 1: Check if Domain → IP → Domain Match
```bash
DOMAIN="google.com"
IP=$(dig +short $DOMAIN | head -1)
REVERSE=$(dig -x $IP +short | sed 's/\.$//')
echo "Original: $DOMAIN"
echo "IP: $IP"
echo "Reverse: $REVERSE"
```

### Tip 2: Find All IPs for a Domain and Their Owners
```bash
DOMAIN="google.com"
for IP in $(dig +short $DOMAIN); do
    echo "=== $IP ==="
    ./whois $IP | grep -E "(OrgName|NetName|Country)" | head -3
    echo ""
done
```

### Tip 3: Trace DNS Resolution Path
```bash
dig +trace google.com
```

### Tip 4: Query Specific DNS Server
```bash
# Use Google DNS
dig @8.8.8.8 google.com

# Use Cloudflare DNS
dig @1.1.1.1 google.com

# Use your local DNS
dig @127.0.0.1 google.com
```

---

## 📊 Tool Comparison

| Feature | Whois | dig | host | nslookup |
|---------|-------|-----|------|----------|
| Domain → IP | ❌ | ✅ Best | ✅ Good | ✅ OK |
| IP → Domain | ❌ | ✅ Best | ✅ Good | ✅ OK |
| Registration Info | ✅ Only tool | ❌ | ❌ | ❌ |
| Network Allocation | ✅ Only tool | ❌ | ❌ | ❌ |
| DNS Records | ❌ | ✅ Best | ✅ Good | ✅ OK |
| Nameservers | ❌ | ✅ | ✅ | ✅ |
| MX Records | ❌ | ✅ | ✅ | ✅ |
| Script-Friendly | ✅ | ✅ Best | ✅ | ❌ |

**Recommendation:** Use `dig` for DNS, `whois` for registration/allocation info

---

## 🎓 Summary

**The Complete Picture:**
1. **DNS tools** (`dig`, `host`) tell you "Where is this domain NOW?" (live data)
2. **Whois** tells you "Who owns this?" and "When was it registered?" (registry data)
3. **Combine both** for complete investigation
4. **Use automated scripts** (`domain_to_info.sh`, `ip_to_info.sh`) for convenience

**Golden Rule:**
- Need current IP/DNS? → Use `dig`
- Need ownership/registration? → Use `whois`
- Need everything? → Use both!
