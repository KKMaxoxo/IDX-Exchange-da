"""
Week 7: Apply outlier filtering to sold and listing datasets.

Transformations:
1. Convert the selected numeric columns to numeric values.
2. Use fixed lower bounds for clearly invalid values:
   - Price: $10,000
   - LivingArea: 80 square feet
   - DaysOnMarket: 0 days
3. Use Q3 + 3 * IQR as the upper bound to flag extreme values while
   reducing the chance of removing valid high-end properties.
4. Add one outlier flag per numeric field and one combined AnyOutlier flag.
5. Save both the full flagged datasets and the filtered datasets.
"""

from pathlib import Path
from datetime import datetime
import re
import pandas as pd
import os
import numpy as np

DATA_DIR = Path("/Users/kmaxx/Desktop/IDX-da/idx_final_data")

sold_df = pd.read_csv(DATA_DIR / "featured_sold.csv", low_memory= False)
listing_df = pd.read_csv(DATA_DIR / "featured_listing.csv", low_memory= False)

#Sold_df
import pandas as pd

outlier_columns = [
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket"
]

lower_bounds = {
    "ClosePrice": 10_000,
    "LivingArea": 80,
    "DaysOnMarket": 0
}

sold_flagged_df = sold_df.copy()

sold_flagged_df[outlier_columns] = sold_flagged_df[
    outlier_columns
].apply(pd.to_numeric, errors="coerce")

outlier_flag_columns = []
outlier_summary = []

for column in outlier_columns:
    q1 = sold_flagged_df[column].quantile(0.25)
    q3 = sold_flagged_df[column].quantile(0.75)
    iqr = q3 - q1

    lower_bound = lower_bounds[column]
    upper_bound = q3 + 3 * iqr

    flag_column = f"{column}_Outlier"
    outlier_flag_columns.append(flag_column)

    sold_flagged_df[flag_column] = (
        sold_flagged_df[column].notna()
        & ~sold_flagged_df[column].between(
            lower_bound,
            upper_bound
        )
    )

    outlier_summary.append({
        "Variable": column,
        "Q1": q1,
        "Q3": q3,
        "IQR": iqr,
        "LowerBound": lower_bound,
        "UpperBound": upper_bound,
        "OutlierCount": sold_flagged_df[flag_column].sum(),
        "OutlierPercentage": (
            sold_flagged_df[flag_column].mean() * 100
        )
    })

outlier_summary = pd.DataFrame(outlier_summary).round(2)

# Keep all rows and add one combined outlier flag
sold_flagged_df["AnyOutlier"] = sold_flagged_df[
    outlier_flag_columns
].any(axis=1)

# Remove rows flagged in at least one variable
sold_no_outliers_df = sold_flagged_df.loc[
    ~sold_flagged_df["AnyOutlier"]
].copy()

print(f"Original rows: {len(sold_df):,}")
print(f"Flagged rows: {sold_flagged_df['AnyOutlier'].sum():,}")
print(f"Rows after removal: {len(sold_no_outliers_df):,}")

derived_columns = [
    "PriceRatio",
    "PricePerSqFt"
]

sold_derived_flagged_df = sold_no_outliers_df.copy()

sold_derived_flagged_df[derived_columns] = sold_derived_flagged_df[
    derived_columns
].apply(pd.to_numeric, errors="coerce").replace(
    [np.inf, -np.inf],
    np.nan
)

derived_flag_columns = []
derived_outlier_summary = []

for column in derived_columns:
    values = sold_derived_flagged_df[column].dropna()

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1

    if column == "PriceRatio":
        lower_bound = q1 - 3 * iqr
    else:
        lower_bound = 50

    upper_bound = q3 + 3 * iqr

    flag_column = f"{column}_Outlier"
    derived_flag_columns.append(flag_column)

    sold_derived_flagged_df[flag_column] = (
        sold_derived_flagged_df[column].notna()
        & ~sold_derived_flagged_df[column].between(
            lower_bound,
            upper_bound
        )
    )

    derived_outlier_summary.append({
        "Variable": column,
        "Q1": q1,
        "Q3": q3,
        "IQR": iqr,
        "LowerBound": lower_bound,
        "UpperBound": upper_bound,
        "OutlierCount": sold_derived_flagged_df[flag_column].sum(),
        "OutlierPercentage": (
            sold_derived_flagged_df[flag_column].mean() * 100
        )
    })

derived_outlier_summary = pd.DataFrame(
    derived_outlier_summary
).round(2)

sold_derived_flagged_df["AnyDerivedOutlier"] = (
    sold_derived_flagged_df[derived_flag_columns].any(axis=1)
)

sold_final_no_outliers_df = sold_derived_flagged_df.loc[
    ~sold_derived_flagged_df["AnyDerivedOutlier"]
].copy()

print(f"Starting rows: {len(sold_no_outliers_df):,}")
print(
    f"PriceRatio outliers: "
    f"{sold_derived_flagged_df['PriceRatio_Outlier'].sum():,}"
)
print(
    f"PricePerSqFt outliers: "
    f"{sold_derived_flagged_df['PricePerSqFt_Outlier'].sum():,}"
)
print(
    f"Total rows flagged: "
    f"{sold_derived_flagged_df['AnyDerivedOutlier'].sum():,}"
)
print(f"Rows retained: {len(sold_final_no_outliers_df):,}")

# Listing_df
import pandas as pd

outlier_columns = [
    "ListPrice",
    "LivingArea",
    "DaysOnMarket"
]

lower_bounds = {
    "ListPrice": 10_000,
    "LivingArea": 80,
    "DaysOnMarket": 0
}

listing_flagged_df = listing_df.copy()

listing_flagged_df[outlier_columns] = listing_flagged_df[
    outlier_columns
].apply(pd.to_numeric, errors="coerce")

outlier_flag_columns = []
outlier_summary = []

for column in outlier_columns:
    q1 = listing_flagged_df[column].quantile(0.25)
    q3 = listing_flagged_df[column].quantile(0.75)
    iqr = q3 - q1

    lower_bound = lower_bounds[column]
    upper_bound = q3 + 3 * iqr

    flag_column = f"{column}_Outlier"
    outlier_flag_columns.append(flag_column)

    listing_flagged_df[flag_column] = (
        listing_flagged_df[column].notna()
        & ~listing_flagged_df[column].between(
            lower_bound,
            upper_bound
        )
    )

    outlier_summary.append({
        "Variable": column,
        "Q1": q1,
        "Q3": q3,
        "IQR": iqr,
        "LowerBound": lower_bound,
        "UpperBound": upper_bound,
        "OutlierCount": listing_flagged_df[flag_column].sum(),
        "OutlierPercentage": listing_flagged_df[flag_column].mean() * 100
    })

listing_outlier_summary = pd.DataFrame(outlier_summary).round(2)

listing_flagged_df["AnyOutlier"] = listing_flagged_df[
    outlier_flag_columns
].any(axis=1)

listing_no_outliers_df = listing_flagged_df.loc[
    ~listing_flagged_df["AnyOutlier"]
].copy()

print(f"Original rows: {len(listing_df):,}")
print(f"Flagged rows: {listing_flagged_df['AnyOutlier'].sum():,}")
print(f"Rows after removal: {len(listing_no_outliers_df):,}")

sold_derived_flagged_df.to_csv(
    DATA_DIR / "sold_derived_outliers_flagged.csv",
    index=False
)

sold_final_no_outliers_df.to_csv(
    DATA_DIR / "sold_final_outliers_removed.csv",
    index=False
)

listing_flagged_df.to_csv(
    DATA_DIR / "listing_outliers_flagged.csv",
    index=False
)

listing_no_outliers_df.to_csv(
    DATA_DIR / "listing_outliers_removed.csv",
    index=False
)
