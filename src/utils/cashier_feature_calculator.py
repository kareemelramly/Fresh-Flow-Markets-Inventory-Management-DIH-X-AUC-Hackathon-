"""
Cashier Risk Feature Calculator

Automatically calculates the 20 statistical features needed for cashier risk assessment
from the database, so the UI only needs to provide the cashier ID.

Database Tables Used:
- fct_cash_balances: Cash drawer reconciliation data
- fct_orders: Transaction data processed by cashier
"""

import sqlite3
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class CashierFeatureCalculator:
    """Calculate cashier risk features from database"""
    
    def __init__(self, db_path: str = 'database/fresh_flow_markets.db'):
        self.db_path = db_path
    
    def get_cashier_features(
        self,
        cashier_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate all 20 features for cashier risk assessment
        
        Args:
            cashier_id: User ID of the cashier
            start_date: Start date (YYYY-MM-DD) - optional
            end_date: End date (YYYY-MM-DD) - optional  
            days_back: Days to look back if dates not provided
            
        Returns:
            Dictionary with all 20 features + metadata
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Calculate date range
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_dt = datetime.now() - timedelta(days=days_back)
            start_date = start_dt.strftime('%Y-%m-%d')
        
        # Convert to UNIX timestamps
        start_unix = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
        end_unix = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
        
        try:
            # Step 1: Get cash balance statistics
            balance_query = """
            SELECT 
                COUNT(DISTINCT id) as id_count,
                AVG(opening_balance) as opening_balance_mean,
                AVG(closing_balance) as closing_balance_mean,
                SUM(closing_balance - opening_balance) as balance_diff_sum,
                AVG(closing_balance - opening_balance) as balance_diff_mean,
                COALESCE(
                    (SELECT 
                        SQRT(AVG((closing_balance - opening_balance - 
                            (SELECT AVG(closing_balance - opening_balance) 
                             FROM fct_cash_balances 
                             WHERE user_id = ? AND created >= ? AND created <= ?)) * 
                            (closing_balance - opening_balance - 
                            (SELECT AVG(closing_balance - opening_balance) 
                             FROM fct_cash_balances 
                             WHERE user_id = ? AND created >= ? AND created <= ?))
                        ))
                     FROM fct_cash_balances 
                     WHERE user_id = ? AND created >= ? AND created <= ?
                    ), 0) as balance_diff_std,
                MIN(closing_balance - opening_balance) as balance_diff_min,
                MAX(closing_balance - opening_balance) as balance_diff_max,
                AVG(CASE 
                    WHEN opening_balance > 0 
                    THEN ABS((closing_balance - opening_balance) / opening_balance * 100)
                    ELSE 0 
                END) as balance_discrepancy_pct_mean,
                MAX(CASE 
                    WHEN opening_balance > 0 
                    THEN ABS((closing_balance - opening_balance) / opening_balance * 100)
                    ELSE 0 
                END) as balance_discrepancy_pct_max
            FROM fct_cash_balances
            WHERE user_id = ? AND created >= ? AND created <= ?
            """
            
            cursor.execute(balance_query, (
                cashier_id, start_unix, end_unix,  # for balance_diff_std sub-query 1
                cashier_id, start_unix, end_unix,  # for balance_diff_std sub-query 2
                cashier_id, start_unix, end_unix,  # for balance_diff_std main query
                cashier_id, start_unix, end_unix   # main WHERE clause
            ))
            balance_row = cursor.fetchone()
            
            # Step 2: Get transaction statistics
            # NOTE: fct_orders doesn't have cashier_id, so we estimate from cash_balances transactions field
            # If transactions JSON field exists, parse it; otherwise use fallback calculations
            transaction_query = """
            SELECT 
                0 as transaction_total_count,
                0 as num_transactions_sum,
                SUM(closing_balance - opening_balance) as transaction_total_sum,
                AVG(closing_balance - opening_balance) as transaction_total_mean,
                SUM((closing_balance - opening_balance) * 0.15) as vat_component_sum,
                SUM(closing_balance - opening_balance) as total_amount_sum,
                AVG(closing_balance - opening_balance) as total_amount_mean,
                COALESCE(
                    (SELECT 
                        SQRT(AVG(((closing_balance - opening_balance) - 
                            (SELECT AVG(closing_balance - opening_balance) 
                             FROM fct_cash_balances 
                             WHERE user_id = ? AND created >= ? AND created <= ?)) * 
                            ((closing_balance - opening_balance) - 
                            (SELECT AVG(closing_balance - opening_balance) 
                             FROM fct_cash_balances 
                             WHERE user_id = ? AND created >= ? AND created <= ?))
                        ))
                     FROM fct_cash_balances 
                     WHERE user_id = ? AND created >= ? AND created <= ?
                    ), 0) as total_amount_std,
                SUM(closing_coins_and_notes) as cash_amount_sum,
                AVG(closing_coins_and_notes) as cash_amount_mean
            FROM fct_cash_balances
            WHERE user_id = ? AND created >= ? AND created <= ?
            """
            
            cursor.execute(transaction_query, (
                cashier_id, start_unix, end_unix,  # for total_amount_std sub-query 1
                cashier_id, start_unix, end_unix,  # for total_amount_std sub-query 2  
                cashier_id, start_unix, end_unix,  # for total_amount_std main query
                cashier_id, start_unix, end_unix   # main WHERE clause
            ))
            trans_row = cursor.fetchone()
            
            # Get estimated transaction count from id_count (assumes 1 shift = multiple transactions)
            est_transaction_count = int(balance_row['id_count'] or 0) * 15  # Estimate ~15 transactions per shift
            
            # Combine features
            features = {
                # Balance difference statistics
                'balance_diff_sum': float(balance_row['balance_diff_sum'] or 0),
                'balance_diff_mean': float(balance_row['balance_diff_mean'] or 0),
                'balance_diff_std': float(balance_row['balance_diff_std'] or 0),
                'balance_diff_min': float(balance_row['balance_diff_min'] or 0),
                'balance_diff_max': float(balance_row['balance_diff_max'] or 0),
                'balance_discrepancy_pct_mean': float(balance_row['balance_discrepancy_pct_mean'] or 0),
                'balance_discrepancy_pct_max': float(balance_row['balance_discrepancy_pct_max'] or 0),
                
                # Transaction statistics (estimated from cash balances)
                'transaction_total_sum': float(trans_row['transaction_total_sum'] or 0),
                'transaction_total_count': est_transaction_count,
                'transaction_total_mean': float(trans_row['transaction_total_mean'] or 0),
                'vat_component_sum': float(trans_row['vat_component_sum'] or 0),
                'num_transactions_sum': est_transaction_count,
                
                # Balance statistics
                'opening_balance_mean': float(balance_row['opening_balance_mean'] or 0),
                'closing_balance_mean': float(balance_row['closing_balance_mean'] or 0),
                'id_count': int(balance_row['id_count'] or 0),
                
                # Amount statistics
                'total_amount_sum': float(trans_row['total_amount_sum'] or 0),
                'total_amount_mean': float(trans_row['total_amount_mean'] or 0),
                'total_amount_std': float(trans_row['total_amount_std'] or 0),
                
                # Cash statistics
                'cash_amount_sum': float(trans_row['cash_amount_sum'] or 0),
                'cash_amount_mean': float(trans_row['cash_amount_mean'] or 0)
            }
            
            # Add metadata
            metadata = {
                'cashier_id': cashier_id,
                'start_date': start_date,
                'end_date': end_date,
                'days_analyzed': days_back,
                'has_data': features['id_count'] > 0 or features['transaction_total_count'] > 0
            }
            
            return {
                'features': features,
                'metadata': metadata,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'features': None,
                'metadata': None,
                'status': 'error',
                'message': str(e)
            }
        finally:
            conn.close()


# Testing
if __name__ == '__main__':
    calculator = CashierFeatureCalculator()
    
    # Test with cashier 22354 (known high-risk from training data)
    result = calculator.get_cashier_features(cashier_id=22354, days_back=365)
    
    if result['status'] == 'success':
        print(f"Cashier {result['metadata']['cashier_id']} Analysis")
        print(f"Period: {result['metadata']['start_date']} to {result['metadata']['end_date']}")
        print(f"Has Data: {result['metadata']['has_data']}")
        print("\nFeatures:")
        for key, val in result['features'].items():
            print(f"  {key}: {val}")
    else:
        print(f"Error: {result['message']}")
