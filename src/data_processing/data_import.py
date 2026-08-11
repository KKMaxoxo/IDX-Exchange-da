"""
Week 1: Combine monthly CRMLS sold and listing files, keep Residential rows,
and save the final combined datasets.
"""

from pathlib import Path
from datetime import datetime
import re
import pandas as pd
import os

DATA_DIR = Path("/Users/kmaxx/Desktop/IDX-da/idx_data")
OUT_DIR = Path("/Users/kmaxx/Desktop/IDX-da/idx_final_data")

SOLD_PREFIX = "CRMLSSold"
LISTING_PREFIX = "CRMLSListing"

combined_sold = pd.DataFrame()
total_before_concat = 0

files = []

for file in Path(DATA_DIR).iterdir():
    if SOLD_PREFIX in file.name:
        df = pd.read_csv(file, low_memory=False)
        if "filled" in file.name: 
            df = df.drop(columns=["latfilled", "lonfilled"], errors="ignore")
        total_before_concat += len(df)
        files.append(df)

combined_sold = pd.concat(files, ignore_index=True)

print(f"Total rows before concatenation: {total_before_concat:,}")
print(f"Total rows after concatenation:  {len(combined_sold):,}")

sold_residential_filter = combined_sold[combined_sold["PropertyType"] == "Residential"]
print(f"Total rows after Residential filter: {len(sold_residential_filter):,}")

combined_listing = pd.DataFrame()
total_before_concat = 0

files = []

for file in Path(DATA_DIR).iterdir():
    if LISTING_PREFIX in file.name:
        df = pd.read_csv(file, low_memory=False)
        if "filled" in file.name: 
            df = df.drop(columns=["latfilled", "lonfilled"], errors="ignore")
        total_before_concat += len(df)
        files.append(df)

combined_listing = pd.concat(files, ignore_index=True)

print(f"Total rows before concatenation: {total_before_concat:,}")
print(f"Total rows after concatenation:  {len(combined_listing):,}")
listing_residential_filter = combined_listing[combined_listing["PropertyType"] == "Residential"]
print(f"Total rows after Residential filter: {len(listing_residential_filter):,}")

sold_residential_filter.to_csv(OUT_DIR / "sold_residential_filter.csv", index=False)
listing_residential_filter.to_csv(OUT_DIR / "listing_residential_filter.csv", index=False)