# 🎬 Demo & Testing Guide

## Quick Demo - Test the System

### **1. Test Individual IPs**

```bash
# Google DNS (well-known company)
curl -s "http://localhost:8001/api/identify/8.8.8.8" | python -m json.tool

Expected: Company="Google", Confidence=80-90%, Method=multi_api_consensus

# Apple (corporate IP block)
curl -s "http://localhost:8001/api/identify/17.172.224.1" | python -m json.tool

Expected: Company="Apple", Confidence=80-95%, Method varies

# Cloudflare
curl -s "http://localhost:8001/api/identify/1.1.1.1" | python -m json.tool

Expected: Company="Cloudflare", Confidence=70-85%

# AWS (Cloud Provider - might show ISP)
curl -s "http://localhost:8001/api/identify/52.34.12.56" | python -m json.tool

Expected: May show "Amazon" (infrastructure) or tenant company
```

### **2. Track a Visitor**

```bash
# Simulate a website visitor
curl -X POST http://localhost:8001/api/track \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "8.8.8.8",
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "referrer": "https://google.com",
    "page_url": "https://yoursite.com/product"
  }' | python -m json.tool

Expected Response:
{
  "success": true,
  "visitor_id": "uuid-here",
  "company_name": "Google",
  "confidence": 0.9,
  "is_isp": false,
  "cached": false
}
```

### **3. View Analytics**

```bash
# Get 7-day analytics
curl -s "http://localhost:8001/api/analytics?days=7" | python -m json.tool

# Get all visitors
curl -s "http://localhost:8001/api/visitors?limit=10" | python -m json.tool

# Get system stats
curl -s "http://localhost:8001/api/stats" | python -m json.tool
```

---

## 🧪 Test All Identification Layers

### **Layer 1: WHOIS Test**

```bash
# Direct WHOIS test (using the original binary)
/app/whois 8.8.8.8 | grep -E "(OrgName|NetName|Organization)"

Expected: Shows "Google LLC" or similar
```

### **Layer 3: Reverse DNS Test**

```bash
# Test reverse DNS
dig -x 8.8.8.8 +short

Expected: dns.google or similar
```

### **Layer 4: ASN Test**

```bash
# Test ASN lookup
whois -h whois.cymru.com " -v 8.8.8.8"

Expected: Shows AS15169 (Google)
```

### **Layer 2: Multi-API Test**

The system automatically queries these in parallel:
- IPinfo.io (50k/month free)
- ipapi.co (30k/month free)  
- ip-api.com (45/min free)

And uses consensus algorithm to choose best result.

---

## 📊 Test Scenarios

### **Scenario 1: Large Enterprise (Best Case)**

```bash
# Test IPs from well-known companies
curl -s "http://localhost:8001/api/identify/8.8.8.8" | jq '.company_name, .confidence, .method'
# Expected: "Google", 0.8-0.9, "multi_api_consensus"

curl -s "http://localhost:8001/api/identify/17.0.0.1" | jq '.company_name, .confidence, .method'
# Expected: "Apple", 0.8-0.95, varies
```

**Expected Accuracy: 85-95%** ✅

---

### **Scenario 2: Cloud/VPN (Medium Difficulty)**

```bash
# AWS IP (might show Amazon or tenant)
curl -s "http://localhost:8001/api/identify/52.34.12.56" | jq '.company_name, .confidence'

# GitHub (uses cloud provider)
curl -s "http://localhost:8001/api/identify/140.82.112.1" | jq '.company_name, .confidence'
```

**Expected Accuracy: 50-70%** ⚠️

---

### **Scenario 3: ISP (Residential - Hard)**

```bash
# Comcast residential IP (example - use real one)
# Will likely show "Comcast" or ISP name
curl -s "http://localhost:8001/api/identify/73.94.0.1" | jq '.company_name, .is_isp'

# Expected: is_isp = true
```

**Expected Accuracy: 10-20%** (Shows ISP, not end user company) ❌

---

## 🎯 Batch Testing

### **Test Multiple IPs at Once**

```bash
# Create test file
cat > /tmp/test_ips.txt << EOF
8.8.8.8
1.1.1.1
17.0.0.1
140.82.112.1
EOF

# Test each IP
while read ip; do
  echo "Testing $ip..."
  curl -s "http://localhost:8001/api/identify/$ip" | jq '{ip, company: .company_name, confidence, method: .method}'
  echo ""
done < /tmp/test_ips.txt
```

---

## 📈 Performance Testing

### **Test Caching**

```bash
# First request (no cache)
time curl -s "http://localhost:8001/api/identify/8.8.8.8?skip_cache=true" > /dev/null

# Second request (should be cached)
time curl -s "http://localhost:8001/api/identify/8.8.8.8" | jq '.cached'

# Expected: Second request is much faster, cached = true
```

### **Test Concurrent Requests**

```bash
# Test 10 concurrent requests
for i in {1..10}; do
  curl -s "http://localhost:8001/api/identify/8.8.8.$i" &
done
wait

echo "All requests completed"
```

---

## 🌐 Frontend Testing

### **1. Access Dashboard**

Open browser: `http://localhost:3000`

**What to check:**
- ✅ Dashboard loads
- ✅ Metrics show data
- ✅ Recent visitors table
- ✅ Top companies chart
- ✅ System status badges

### **2. Test IP Lookup Tool**

1. Go to "IP Lookup" tab
2. Enter: `8.8.8.8`
3. Click "Lookup"

**Expected:**
- Company name shown
- Confidence score displayed
- All layer results visible
- Location data shown

### **3. Test Real-Time Updates**

1. In terminal, track some visitors:
```bash
for ip in 8.8.8.8 1.1.1.1 17.0.0.1; do
  curl -X POST http://localhost:8001/api/track \
    -H "Content-Type: application/json" \
    -d "{\"ip_address\": \"$ip\"}"
  sleep 1
done
```

2. In browser, click "Refresh" button
3. Check if new visitors appear

---

## 🔍 Debugging Tests

### **Check Backend Health**

```bash
# Test root endpoint
curl http://localhost:8001/

# Expected: Returns API info
```

### **Check MongoDB Connection**

```bash
# Check if visitors are being saved
mongo visitor_tracker --eval "db.visitors.count()"

# View recent visitors
mongo visitor_tracker --eval "db.visitors.find().sort({timestamp: -1}).limit(3).pretty()"
```

### **Check Cache Stats**

```bash
curl -s http://localhost:8001/api/stats | jq '.cache_stats'

# Expected: Shows cached IPs count
```

### **Check Logs**

```bash
# Backend logs
tail -f /var/log/supervisor/backend.err.log

# Frontend logs
tail -f /var/log/supervisor/frontend.out.log
```

---

## 🎨 Test Tracking Integration

### **Create Test HTML Page**

```bash
cat > /tmp/test-tracking.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <title>Tracking Test</title>
</head>
<body>
  <h1>Visitor Tracking Test Page</h1>
  <p>Open browser console to see tracking results.</p>
  
  <script>
    (function() {
      var apiUrl = 'http://localhost:8001';
      
      // Track visitor
      fetch(apiUrl + '/api/track', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          user_agent: navigator.userAgent,
          referrer: document.referrer,
          page_url: window.location.href
        })
      })
      .then(res => res.json())
      .then(data => {
        console.log('Visitor tracked:', data);
        document.body.innerHTML += '<div style="margin-top: 20px; padding: 20px; background: #e0f7fa; border-radius: 8px;">' +
          '<h2>Tracking Result</h2>' +
          '<p><strong>Company:</strong> ' + (data.company_name || 'Unknown') + '</p>' +
          '<p><strong>Confidence:</strong> ' + Math.round(data.confidence * 100) + '%</p>' +
          '<p><strong>Is ISP:</strong> ' + data.is_isp + '</p>' +
          '<p><strong>Cached:</strong> ' + data.cached + '</p>' +
          '</div>';
      })
      .catch(err => console.error('Tracking error:', err));
    })();
  </script>
</body>
</html>
EOF

# Open in browser
echo "Open file:///tmp/test-tracking.html in your browser"
```

---

## ✅ Success Criteria

Your system is working correctly if:

1. **Backend Health:**
   - ✅ API responds at http://localhost:8001
   - ✅ Can identify Google (8.8.8.8) with 80%+ confidence
   - ✅ Multi-API consensus working
   - ✅ Caching reduces response time

2. **Frontend Health:**
   - ✅ Dashboard loads at http://localhost:3000
   - ✅ Real-time data updates
   - ✅ IP lookup tool works
   - ✅ Analytics show charts

3. **Data Flow:**
   - ✅ Tracking endpoint saves to MongoDB
   - ✅ Visitors appear in dashboard
   - ✅ Analytics calculate correctly

4. **Identification Accuracy:**
   - ✅ Large companies: 80%+ identification
   - ✅ Multi-API consensus: 2+ APIs agree
   - ✅ ISP detection works (flags residential IPs)

---

## 🐛 Common Issues

### **Issue: Low confidence scores**
**Solution:** Add API keys to .env file and restart backend

### **Issue: "No company found"**
**Solution:** Normal for residential IPs. Test with known corporate IPs first.

### **Issue: Frontend can't connect**
**Solution:** Check REACT_APP_BACKEND_URL in frontend/.env

### **Issue: Slow responses**
**Solution:** Check if caching is enabled. First lookup is slow, subsequent should be fast.

---

## 🎉 Quick Verification

Run this one command to test everything:

```bash
# Test identification
curl -s "http://localhost:8001/api/identify/8.8.8.8" | jq '{company: .company_name, confidence, layers: [.all_results[].method]}'

# Track a visitor
curl -X POST http://localhost:8001/api/track -H "Content-Type: application/json" -d '{"ip_address": "8.8.8.8"}' | jq .

# Check analytics
curl -s "http://localhost:8001/api/analytics?days=7" | jq '{visitors: .total_visitors, identified: .identified_visitors, rate: .identification_rate}'
```

If all three commands work, your system is fully operational! 🚀
