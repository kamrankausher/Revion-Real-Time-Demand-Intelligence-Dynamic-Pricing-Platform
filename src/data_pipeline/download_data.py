import os
import zipfile
import pandas as pd
import numpy as np
from pathlib import Path
from src.config import RAW_DATA_DIR

def download_from_kaggle():
    print("Attempting to download from Kaggle...")
    try:
        import kaggle
        kaggle.api.authenticate()
        kaggle.api.competition_download_files('m5-forecasting-accuracy', path=RAW_DATA_DIR)
        
        zip_path = RAW_DATA_DIR / 'm5-forecasting-accuracy.zip'
        if zip_path.exists():
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(RAW_DATA_DIR)
            os.remove(zip_path)
            print("Successfully downloaded and extracted M5 data.")
            return True
    except Exception as e:
        print(f"Kaggle download failed: {e}")
        return False
    return False

def generate_synthetic_m5():
    print("Generating synthetic M5 dataset for testing...")
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate Calendar
    dates = pd.date_range('2011-01-29', periods=1941, freq='D')
    calendar = pd.DataFrame({
        'date': dates,
        'wm_yr_wk': 11101 + np.arange(1941) // 7,
        'weekday': dates.day_name(),
        'wday': dates.dayofweek + 1,
        'month': dates.month,
        'year': dates.year,
        'd': [f"d_{i}" for i in range(1, 1942)],
        'event_name_1': np.nan,
        'event_type_1': np.nan,
        'event_name_2': np.nan,
        'event_type_2': np.nan,
        'snap_CA': np.random.choice([0, 1], size=1941, p=[0.7, 0.3]),
        'snap_TX': np.random.choice([0, 1], size=1941, p=[0.7, 0.3]),
        'snap_WI': np.random.choice([0, 1], size=1941, p=[0.7, 0.3])
    })
    calendar.to_csv(RAW_DATA_DIR / 'calendar.csv', index=False)
    
    # Generate Sales
    # 5 items, 2 stores
    items = ["FOODS_3_090", "HOBBIES_1_001", "HOUSEHOLD_2_005", "FOODS_1_001", "FOODS_2_011"]
    depts = ["FOODS_3", "HOBBIES_1", "HOUSEHOLD_2", "FOODS_1", "FOODS_2"]
    cats = ["FOODS", "HOBBIES", "HOUSEHOLD", "FOODS", "FOODS"]
    stores = ["CA_1", "TX_1"]
    states = ["CA", "TX"]
    
    rows = []
    for store, state in zip(stores, states):
        for item, dept, cat in zip(items, depts, cats):
            row = {
                'id': f"{item}_{store}_validation",
                'item_id': item,
                'dept_id': dept,
                'cat_id': cat,
                'store_id': store,
                'state_id': state
            }
            # Sales data for 1913 days
            sales = np.random.poisson(lam=5, size=1913)
            for i, s in enumerate(sales):
                row[f'd_{i+1}'] = s
            rows.append(row)
            
    sales_df = pd.DataFrame(rows)
    sales_df.to_csv(RAW_DATA_DIR / 'sales_train_validation.csv', index=False)
    
    # Evaluation
    eval_rows = []
    for r in rows:
        eval_row = r.copy()
        eval_row['id'] = r['id'].replace('validation', 'evaluation')
        sales_eval = np.random.poisson(lam=5, size=28)
        for i, s in enumerate(sales_eval):
            eval_row[f'd_{1913+i+1}'] = s
        eval_rows.append(eval_row)
    sales_eval_df = pd.DataFrame(eval_rows)
    sales_eval_df.to_csv(RAW_DATA_DIR / 'sales_train_evaluation.csv', index=False)
    
    # Generate Sell Prices
    prices = []
    unique_yr_wk = calendar['wm_yr_wk'].unique()
    for store in stores:
        for item in items:
            base_price = np.random.uniform(1.0, 10.0)
            for wk in unique_yr_wk:
                prices.append({
                    'store_id': store,
                    'item_id': item,
                    'wm_yr_wk': wk,
                    'sell_price': round(base_price + np.random.normal(0, 0.5), 2)
                })
    prices_df = pd.DataFrame(prices)
    prices_df.to_csv(RAW_DATA_DIR / 'sell_prices.csv', index=False)
    print("Synthetic data generated successfully.")

if __name__ == "__main__":
    generate_synthetic_m5()
