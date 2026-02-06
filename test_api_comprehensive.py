"""
Comprehensive API Test Suite
Tests all API endpoints including ML predictions, standard API, and database integration
"""

import requests
import json
from datetime import datetime, timedelta
import time

# Configuration
API_BASE_URL = "http://localhost:5000"
API_URL = f"{API_BASE_URL}/api"
ML_API_URL = f"{API_BASE_URL}/api/ml"

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.RESET}\n")

def print_test(test_name, passed, details=""):
    """Print test result"""
    status = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if passed else f"{Colors.RED}❌ FAIL{Colors.RESET}"
    print(f"{status} - {test_name}")
    if details:
        print(f"      {Colors.YELLOW}{details}{Colors.RESET}")

def test_api_health():
    """Test API health endpoints"""
    print_header("API HEALTH CHECKS")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Root endpoint
    tests_total += 1
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        passed = response.status_code == 200 and 'service' in response.json()
        print_test("Root endpoint (/)", passed, f"Status: {response.status_code}")
        if passed:
            tests_passed += 1
            data = response.json()
            print(f"      Service: {data.get('service')}, Version: {data.get('version')}")
    except Exception as e:
        print_test("Root endpoint (/)", False, str(e))
    
    # Test 2: Health endpoint
    tests_total += 1
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        passed = response.status_code == 200 and response.json().get('status') == 'healthy'
        print_test("Health endpoint (/health)", passed, f"Database: {response.json().get('database')}")
        if passed:
            tests_passed += 1
    except Exception as e:
        print_test("Health endpoint (/health)", False, str(e))
    
    # Test 3: ML Health endpoint
    tests_total += 1
    try:
        response = requests.get(f"{ML_API_URL}/health", timeout=5)
        passed = response.status_code == 200 and 'service' in response.json()
        print_test("ML Health endpoint (/api/ml/health)", passed, f"Status: {response.json().get('status')}")
        if passed:
            tests_passed += 1
    except Exception as e:
        print_test("ML Health endpoint (/api/ml/health)", False, str(e))
    
    # Test 4: ML Models Status
    tests_total += 1
    try:
        response = requests.get(f"{ML_API_URL}/models/status", timeout=5)
        passed = response.status_code == 200 and response.json().get('success')
        print_test("ML Models Status (/api/ml/models/status)", passed)
        if passed:
            tests_passed += 1
            models = response.json().get('models', {})
            for model_name, model_info in models.items():
                available = "✅" if model_info.get('available') else "⏳"
                print(f"      {available} {model_info.get('name')}")
    except Exception as e:
        print_test("ML Models Status (/api/ml/models/status)", False, str(e))
    
    return tests_passed, tests_total

def test_inventory_api():
    """Test inventory management endpoints"""
    print_header("INVENTORY API TESTS")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Get inventory items
    tests_total += 1
    try:
        response = requests.get(f"{API_URL}/inventory/items", params={'page': 1, 'per_page': 10}, timeout=5)
        passed = response.status_code == 200 and response.json().get('success')
        data = response.json()
        item_count = len(data.get('data', []))
        print_test("Get inventory items", passed, f"Retrieved {item_count} items")
        if passed:
            tests_passed += 1
    except Exception as e:
        print_test("Get inventory items", False, str(e))
    
    # Test 2: Get low stock items
    tests_total += 1
    try:
        response = requests.get(f"{API_URL}/inventory/low-stock", timeout=5)
        passed = response.status_code == 200 and response.json().get('success')
        count = response.json().get('count', 0)
        print_test("Get low stock items", passed, f"Found {count} low stock items")
        if passed:
            tests_passed += 1
    except Exception as e:
        print_test("Get low stock items", False, str(e))
    
    # Test 3: Get single item (if items exist)
    tests_total += 1
    try:
        # First get an item ID
        response = requests.get(f"{API_URL}/inventory/items", params={'per_page': 1}, timeout=5)
        if response.json().get('data'):
            item_id = response.json()['data'][0]['id']
            response = requests.get(f"{API_URL}/inventory/items/{item_id}", timeout=5)
            passed = response.status_code == 200 and response.json().get('success')
            print_test(f"Get item details (ID: {item_id})", passed)
            if passed:
                tests_passed += 1
        else:
            print_test("Get item details", False, "No items in database")
    except Exception as e:
        print_test("Get item details", False, str(e))
    
    return tests_passed, tests_total

def test_orders_api():
    """Test orders endpoints"""
    print_header("ORDERS API TESTS")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Get orders
    tests_total += 1
    try:
        response = requests.get(f"{API_URL}/orders", params={'page': 1, 'per_page': 10}, timeout=5)
        passed = response.status_code == 200 and response.json().get('success')
        data = response.json()
        order_count = len(data.get('data', []))
        print_test("Get orders list", passed, f"Retrieved {order_count} orders")
        if passed:
            tests_passed += 1
    except Exception as e:
        print_test("Get orders list", False, str(e))
    
    # Test 2: Get single order
    tests_total += 1
    try:
        response = requests.get(f"{API_URL}/orders", params={'per_page': 1}, timeout=5)
        if response.json().get('data'):
            order_id = response.json()['data'][0]['id']
            response = requests.get(f"{API_URL}/orders/{order_id}", timeout=5)
            passed = response.status_code == 200 and response.json().get('success')
            print_test(f"Get order details (ID: {order_id})", passed)
            if passed:
                tests_passed += 1
                items_count = len(response.json()['data'].get('items', []))
                print(f"      Order has {items_count} items")
        else:
            print_test("Get order details", False, "No orders in database")
    except Exception as e:
        print_test("Get order details", False, str(e))
    
    return tests_passed, tests_total

def test_analytics_api():
    """Test analytics endpoints"""
    print_header("ANALYTICS API TESTS")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Dashboard stats
    tests_total += 1
    try:
        response = requests.get(f"{API_URL}/analytics/dashboard", params={'days': 30}, timeout=5)
        passed = response.status_code == 200 and response.json().get('success')
        print_test("Dashboard statistics", passed)
        if passed:
            tests_passed += 1
            data = response.json()['data']
            summary = data.get('summary', {})
            print(f"      Total Orders: {summary.get('total_orders', 0)}")
            print(f"      Total Revenue: {summary.get('total_revenue', 0):.2f} DKK")
    except Exception as e:
        print_test("Dashboard statistics", False, str(e))
    
    # Test 2: Places analytics
    tests_total += 1
    try:
        response = requests.get(f"{API_URL}/analytics/places", params={'days': 30}, timeout=5)
        passed = response.status_code == 200 and response.json().get('success')
        places_count = len(response.json().get('data', []))
        print_test("Places analytics", passed, f"Analyzed {places_count} places")
        if passed:
            tests_passed += 1
    except Exception as e:
        print_test("Places analytics", False, str(e))
    
    return tests_passed, tests_total

def test_campaign_ml_api():
    """Test Campaign ROI ML endpoints"""
    print_header("CAMPAIGN ROI ML TESTS")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Campaign prediction
    tests_total += 1
    try:
        payload = {
            "duration_days": 7,
            "points": 200,
            "discount_percent": 20,
            "minimum_spend": 100
        }
        response = requests.post(f"{ML_API_URL}/campaigns/predict", json=payload, timeout=10)
        passed = response.status_code == 200 and response.json().get('success')
        
        if passed:
            data = response.json()['data']
            if data.get('status') == 'success':
                predictions = data['predictions']
                print_test("Campaign prediction", True, 
                          f"Redemptions: {predictions['expected_redemptions']}, "
                          f"Success: {predictions['success_probability']}%")
                print(f"      Recommendation: {data['recommendation']['action']}")
                tests_passed += 1
            elif data.get('status') == 'model_not_ready':
                print_test("Campaign prediction", False, "Model not yet trained")
            else:
                print_test("Campaign prediction", False, f"Unexpected status: {data.get('status')}")
        else:
            print_test("Campaign prediction", False, f"Status code: {response.status_code}")
    except Exception as e:
        print_test("Campaign prediction", False, str(e))
    
    # Test 2: Campaign optimization
    tests_total += 1
    try:
        payload = {
            "target_redemptions": 25,
            "max_discount": 30,
            "budget_per_redemption": 100
        }
        response = requests.post(f"{ML_API_URL}/campaigns/optimize", json=payload, timeout=15)
        passed = response.status_code == 200 and response.json().get('success')
        
        if passed:
            data = response.json()['data']
            if data.get('status') == 'success':
                optimal = data['optimal_parameters']
                print_test("Campaign optimization", True,
                          f"Optimal: {optimal['duration_days']}d, {optimal['points']}pts, "
                          f"{optimal['discount_percent']}% off")
                tests_passed += 1
            else:
                print_test("Campaign optimization", False, data.get('message', 'Unknown error'))
        else:
            print_test("Campaign optimization", False, f"Status code: {response.status_code}")
    except Exception as e:
        print_test("Campaign optimization", False, str(e))
    
    # Test 3: Batch campaign prediction
    tests_total += 1
    try:
        payload = {
            "campaigns": [
                {"duration_days": 3, "points": 100, "discount_percent": 10, "minimum_spend": 50},
                {"duration_days": 7, "points": 200, "discount_percent": 20, "minimum_spend": 100},
                {"duration_days": 14, "points": 500, "discount_percent": 30, "minimum_spend": 200}
            ]
        }
        response = requests.post(f"{ML_API_URL}/campaigns/batch-predict", json=payload, timeout=15)
        passed = response.status_code == 200 and response.json().get('success')
        
        if passed:
            data = response.json()
            print_test("Batch campaign prediction", True, 
                      f"Compared {data['total_campaigns']} campaigns")
            if data.get('best_campaign'):
                best = data['best_campaign']
                print(f"      Best campaign: Index {best.get('campaign_index')}, "
                      f"Success: {best['predictions']['success_probability']}%")
            tests_passed += 1
        else:
            print_test("Batch campaign prediction", False, f"Status code: {response.status_code}")
    except Exception as e:
        print_test("Batch campaign prediction", False, str(e))
    
    return tests_passed, tests_total

def test_demand_ml_api():
    """Test Demand Forecasting ML endpoints"""
    print_header("DEMAND FORECASTING ML TESTS")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Demand forecast
    tests_total += 1
    try:
        payload = {
            "item_id": 1,
            "forecast_days": 7,
            "campaign_active": False
        }
        response = requests.post(f"{ML_API_URL}/forecast/demand", json=payload, timeout=10)
        passed = response.status_code == 200 and response.json().get('success')
        
        if passed:
            data = response.json()['data']
            if data.get('status') == 'success':
                print_test("Demand forecast", True, 
                          f"7-day forecast: {data['summary']['total_predicted_demand']:.1f} units")
                tests_passed += 1
            elif data.get('status') == 'model_not_ready':
                print_test("Demand forecast", False, "Model not yet trained ⏳")
            else:
                print_test("Demand forecast", False, data.get('message', 'Unknown status'))
        else:
            print_test("Demand forecast", False, f"Status code: {response.status_code}")
    except Exception as e:
        print_test("Demand forecast", False, str(e))
    
    # Test 2: Reorder recommendations
    tests_total += 1
    try:
        payload = {
            "item_id": 1,
            "current_stock": 50,
            "lead_time_days": 3
        }
        response = requests.post(f"{ML_API_URL}/forecast/reorder-recommendations", json=payload, timeout=10)
        passed = response.status_code == 200 and response.json().get('success')
        
        if passed:
            data = response.json()['data']
            if data.get('status') == 'success':
                recs = data['recommendations']
                print_test("Reorder recommendations", True,
                          f"Reorder needed: {recs['reorder_needed']}, "
                          f"Urgency: {recs['urgency']}")
                tests_passed += 1
            else:
                print_test("Reorder recommendations", False, data.get('message', 'Model not ready'))
        else:
            print_test("Reorder recommendations", False, f"Status code: {response.status_code}")
    except Exception as e:
        print_test("Reorder recommendations", False, str(e))
    
    return tests_passed, tests_total

def test_churn_ml_api():
    """Test Customer Churn ML endpoints"""
    print_header("CUSTOMER CHURN ML TESTS")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Churn risk prediction
    tests_total += 1
    try:
        payload = {
            "customer_id": 123,
            "recent_waiting_time": 35,
            "recent_rating": 2.5,
            "points_redeemed": 150,
            "vip_threshold": 1000,
            "days_since_last_order": 25
        }
        response = requests.post(f"{ML_API_URL}/customers/churn-risk", json=payload, timeout=10)
        passed = response.status_code == 200 and response.json().get('success')
        
        if passed:
            data = response.json()['data']
            if data.get('status') == 'success':
                risk = data['churn_risk']
                print_test("Churn risk prediction", True,
                          f"Churn probability: {risk['probability']}%, "
                          f"Level: {risk['level']}")
                tests_passed += 1
            else:
                print_test("Churn risk prediction", False, data.get('message', 'Model not ready'))
        else:
            print_test("Churn risk prediction", False, f"Status code: {response.status_code}")
    except Exception as e:
        print_test("Churn risk prediction", False, str(e))
    
    return tests_passed, tests_total

def test_cashier_ml_api():
    """Test Cashier Risk ML endpoints"""
    print_header("CASHIER RISK ML TESTS")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Cashier risk detection
    tests_total += 1
    try:
        payload = {
            "cashier_id": 45,
            "shift_date": "2026-02-05",
            "order_count": 150,
            "expected_balance": 15000.00,
            "actual_balance": 14850.00,
            "total_vat": 3000.00
        }
        response = requests.post(f"{ML_API_URL}/operations/cashier-risk", json=payload, timeout=10)
        passed = response.status_code == 200 and response.json().get('success')
        
        if passed:
            data = response.json()['data']
            if data.get('status') == 'success':
                risk = data['risk_assessment']
                print_test("Cashier risk detection", True,
                          f"Risk score: {risk['risk_score']:.3f}, "
                          f"Level: {risk['risk_level']}")
                tests_passed += 1
            else:
                print_test("Cashier risk detection", False, data.get('message', 'Model not ready'))
        else:
            print_test("Cashier risk detection", False, f"Status code: {response.status_code}")
    except Exception as e:
        print_test("Cashier risk detection", False, str(e))
    
    return tests_passed, tests_total

def run_all_tests():
    """Run all API tests"""
    print_header("FRESH FLOW MARKETS - COMPREHENSIVE API TEST SUITE")
    print(f"{Colors.BOLD}Testing API at: {API_BASE_URL}{Colors.RESET}")
    print(f"{Colors.BOLD}Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    
    # Check if server is running
    try:
        requests.get(API_BASE_URL, timeout=2)
    except requests.exceptions.ConnectionError:
        print(f"\n{Colors.RED}❌ ERROR: API server is not running!{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Please start the server first:{Colors.RESET}")
        print(f"   python app.py")
        print(f"\nThen run this test suite again.")
        return
    
    all_results = []
    
    # Run all test suites
    all_results.append(("API Health", test_api_health()))
    all_results.append(("Inventory API", test_inventory_api()))
    all_results.append(("Orders API", test_orders_api()))
    all_results.append(("Analytics API", test_analytics_api()))
    all_results.append(("Campaign ML", test_campaign_ml_api()))
    all_results.append(("Demand ML", test_demand_ml_api()))
    all_results.append(("Churn ML", test_churn_ml_api()))
    all_results.append(("Cashier ML", test_cashier_ml_api()))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    total_passed = 0
    total_tests = 0
    
    for suite_name, (passed, total) in all_results:
        total_passed += passed
        total_tests += total
        
        percentage = (passed / total * 100) if total > 0 else 0
        color = Colors.GREEN if percentage == 100 else Colors.YELLOW if percentage >= 50 else Colors.RED
        
        print(f"{color}{suite_name:30} {passed:>3}/{total:<3} tests passed ({percentage:>5.1f}%){Colors.RESET}")
    
    print(f"\n{Colors.BOLD}{'=' * 80}{Colors.RESET}")
    
    overall_percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
    overall_color = Colors.GREEN if overall_percentage >= 80 else Colors.YELLOW if overall_percentage >= 50 else Colors.RED
    
    print(f"{Colors.BOLD}OVERALL RESULT: "
          f"{overall_color}{total_passed}/{total_tests} tests passed ({overall_percentage:.1f}%){Colors.RESET}")
    
    if overall_percentage == 100:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! API IS FULLY OPERATIONAL!{Colors.RESET}")
    elif overall_percentage >= 80:
        print(f"\n{Colors.YELLOW}⚠️  Most tests passed. Check failures above.{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}❌ Many tests failed. Check API server and database.{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 80}{Colors.RESET}\n")

if __name__ == "__main__":
    run_all_tests()
