# Global Patent Intelligence Data Pipeline

A data pipeline that collects, cleans, stores, and analyzes real-world patent data from USPTO PatentsView.

## Setup
1. Clone this repo
2. Run `pip install -r requirements.txt`
3. Run `python scripts/download_data.py`
4. Run `python scripts/clean_data.py`
5. Run `python scripts/load_data.py`
6. Run `python scripts/report.py`