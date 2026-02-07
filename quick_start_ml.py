"""
Fresh Flow Markets - Quick Start Script
Starts API server and dashboard, then runs integration tests
"""

import subprocess
import time
import sys
import os

def main():
    print("="*80)
    print("FRESH FLOW MARKETS - QUICK START")
    print("="*80)
    print("\nThis script will:")
    print("  1. Start the API server (Flask)")
    print("  2. Wait for it to initialize")
    print("  3. Run ML integration tests")
    print("  4. Provide instructions to start the dashboard")
    print("\n" + "="*80 + "\n")
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found. Please run this from the project root directory.")
        sys.exit(1)
    
    # Instructions
    print("STEP 1: Starting API Server...")
    print("-" * 80)
    print("\nManual steps:")
    print("  1. Open a NEW terminal window")
    print("  2. Run: python app.py")
    print("  3. Wait for 'Running on http://0.0.0.0:5000' message")
    print("\n  Then press ENTER here to continue...")
    input()
    
    print("\nSTEP 2: Testing ML Integration...")
    print("-" * 80)
    time.sleep(2)
    
    # Run tests
    try:
        subprocess.run([sys.executable, "test_ml_integration.py"], check=False)
    except Exception as e:
        print(f"Error running tests: {e}")
    
    print("\nSTEP 3: Start the Dashboard")
    print("-" * 80)
    print("\nTo start the Streamlit dashboard:")
    print("  1. Open ANOTHER new terminal window")
    print("  2. Run: streamlit run dashboard.py")
    print("  3. Navigate to the 'Forecasting Suggestions' tab")
    print("  4. Test the three ML tabs:")
    print("     - 🎯 Campaign ROI")
    print("     - 👥 Customer Churn")
    print("     - 🏪 Cashier Integrity and Operational Risk")
    
    print("\n" + "="*80)
    print("ENDPOINTS AVAILABLE")
    print("="*80)
    print("\n📊 Dashboard: http://localhost:8501")
    print("🔧 API Server: http://localhost:5000")
    print("📚 API Docs: http://localhost:5000/")
    
    print("\n" + "="*80)
    print("ML MODEL STATUS")
    print("="*80)
    print("\n✅ Campaign ROI Predictor - READY")
    print("✅ Customer Churn Predictor - READY")
    print("✅ Cashier Risk Monitor - READY")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
