Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host "FRESH FLOW MARKETS - SYSTEM STATUS" -ForegroundColor Yellow
Write-Host ("=" * 80) -ForegroundColor Cyan

$url = "http://localhost:5000"
$passed = 0
$total = 7

# Test 1: Health
Write-Host "`n1. API Health... " -NoNewline
try {
    $response = curl.exe -s -X GET "$url/health"
    if ($response -match "healthy") {
        Write-Host "✅" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "❌" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error" -ForegroundColor Red
}

# Test 2: Database Orders
Write-Host "2. Database... " -NoNewline
try {
    $response = curl.exe -s -X GET "$url/health"
    if ($response -match '"orders_count":\s*(\d+)') {
        $orders = $matches[1]
        Write-Host "✅ $orders orders" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "❌" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error" -ForegroundColor Red
}

# Test 3: Inventory API
Write-Host "3. Inventory API... " -NoNewline
try {
    $response = curl.exe -s -w "%{http_code}" -X GET "$url/api/inventory/items?page=1&per_page=1"
    if ($response -match "200$") {
        Write-Host "✅" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "❌" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error" -ForegroundColor Red
}

# Test 4: Orders API
Write-Host "4. Orders API... " -NoNewline
try {
    $response = curl.exe -s -w "%{http_code}" -X GET "$url/api/orders?page=1&per_page=1"
    if ($response -match "200$") {
        Write-Host "✅" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "❌" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error" -ForegroundColor Red
}

# Test 5: ML Service
Write-Host "5. ML Service... " -NoNewline
try {
    $response = curl.exe -s -X GET "$url/api/ml/health"
    if ($response -match '"ready_models":\s*(\d+)') {
        $models = $matches[1]
        Write-Host "✅ $models/4 models ready" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "❌" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error" -ForegroundColor Red
}

# Test 6: Campaign ROI Prediction
Write-Host "6. Campaign ML Prediction... " -NoNewline
try {
    $body = '{"duration_days":30,"points":50,"discount_percent":10,"minimum_spend":100}'
    $response = curl.exe -s -X POST "$url/api/ml/campaigns/predict" -H "Content-Type: application/json" -d $body
    if ($response -match '"expected_redemptions":\s*([\d.]+)') {
        $redemptions = $matches[1]
        Write-Host "✅ Predicts $redemptions redemptions" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "❌" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error" -ForegroundColor Red
}

# Test 7: CORS
Write-Host "7. CORS (Web Integration)... " -NoNewline
try {
    $headers = curl.exe -s -I -X OPTIONS "$url/api/ml/campaigns/predict"
    if ($headers -match "Access-Control-Allow-Origin") {
        Write-Host "✅ Enabled" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "❌" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error" -ForegroundColor Red
}

# Summary
$percentage = [math]::Round(($passed / $total) * 100)
Write-Host "`n" -NoNewline
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "RESULT: $passed/$total tests passed ($percentage%)" -ForegroundColor $(if ($percentage -ge 80) { "Green" } else { "Yellow" })
Write-Host ("=" * 80) -ForegroundColor Cyan
