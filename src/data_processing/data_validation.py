"""
Week 2: Review property types, filter to Residential properties, identify
high-missing columns, summarize numeric fields, and save cleaned datasets.
"""

from pathlib import Path

import pandas as pd


DATA_DIR = Path("/Users/kmaxx/Desktop/IDX-da/idx_final_data")

sold_df = pd.read_csv(
    DATA_DIR / "sold_residential_filter.csv",
    low_memory=False
)

listing_df = pd.read_csv(
    DATA_DIR / "listing_residential_filter.csv",
    low_memory=False
)


# --------------------------------------------------
# UNIQUE PROPERTY TYPES
# --------------------------------------------------

sold_property_types = (
    sold_df["PropertyType"]
    .value_counts(dropna=False)
    .rename_axis("PropertyType")
    .reset_index(name="Count")
)

listing_property_types = (
    listing_df["PropertyType"]
    .value_counts(dropna=False)
    .rename_axis("PropertyType")
    .reset_index(name="Count")
)

print("\n" + "-" * 60)
print("SOLD PROPERTY TYPES")
print("-" * 60)
print(sold_property_types.to_string(index=False))

print("\n" + "-" * 60)
print("LISTING PROPERTY TYPES")
print("-" * 60)
print(listing_property_types.to_string(index=False))


# --------------------------------------------------
# FILTERING LOGIC
# --------------------------------------------------

print("\n" + "-" * 60)
print("FILTERING LOGIC")
print("-" * 60)
print("1. Keep rows where PropertyType == 'Residential'.")
print("2. Flag columns with more than 90% null values.")
print("3. Remove columns with more than 90% null values.")

sold_filtered = sold_df.loc[
    sold_df["PropertyType"].eq("Residential")
].copy()

listing_filtered = listing_df.loc[
    listing_df["PropertyType"].eq("Residential")
].copy()


# --------------------------------------------------
# NULL-COUNT AND MISSING-VALUE REPORTS
# --------------------------------------------------

sold_missing_report = pd.DataFrame({
    "Column": sold_filtered.columns,
    "NullCount": sold_filtered.isna().sum().values,
    "NullPercent": (sold_filtered.isna().mean().values * 100).round(2)
})

sold_missing_report["Above90PercentNull"] = (
    sold_missing_report["NullPercent"] > 90
)

sold_missing_report = sold_missing_report.sort_values(
    "NullPercent",
    ascending=False
).reset_index(drop=True)


listing_missing_report = pd.DataFrame({
    "Column": listing_filtered.columns,
    "NullCount": listing_filtered.isna().sum().values,
    "NullPercent": (listing_filtered.isna().mean().values * 100).round(2)
})

listing_missing_report["Above90PercentNull"] = (
    listing_missing_report["NullPercent"] > 90
)

listing_missing_report = listing_missing_report.sort_values(
    "NullPercent",
    ascending=False
).reset_index(drop=True)


print("\n" + "-" * 90)
print("SOLD NULL-COUNT SUMMARY")
print("-" * 90)
print(sold_missing_report.to_string(index=False))

print("\n" + "-" * 90)
print("LISTING NULL-COUNT SUMMARY")
print("-" * 90)
print(listing_missing_report.to_string(index=False))


print("\n" + "-" * 90)
print("SOLD COLUMNS ABOVE 90% NULL")
print("-" * 90)
print(
    sold_missing_report.loc[
        sold_missing_report["Above90PercentNull"]
    ].to_string(index=False)
)

print("\n" + "-" * 90)
print("LISTING COLUMNS ABOVE 90% NULL")
print("-" * 90)
print(
    listing_missing_report.loc[
        listing_missing_report["Above90PercentNull"]
    ].to_string(index=False)
)


sold_columns_to_drop = sold_missing_report.loc[
    sold_missing_report["Above90PercentNull"],
    "Column"
].tolist()

listing_columns_to_drop = listing_missing_report.loc[
    listing_missing_report["Above90PercentNull"],
    "Column"
].tolist()

sold_clean = sold_filtered.drop(
    columns=sold_columns_to_drop
)

listing_clean = listing_filtered.drop(
    columns=listing_columns_to_drop
)


# --------------------------------------------------
# NUMERIC DISTRIBUTION SUMMARY
# --------------------------------------------------

numeric_columns = [
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket"
]

sold_numeric = sold_clean[
    [column for column in numeric_columns if column in sold_clean.columns]
].apply(pd.to_numeric, errors="coerce")

listing_numeric = listing_clean[
    [column for column in numeric_columns if column in listing_clean.columns]
].apply(pd.to_numeric, errors="coerce")

sold_numeric_summary = sold_numeric.describe(
    percentiles=[
        0.01,
        0.05,
        0.25,
        0.50,
        0.75,
        0.95,
        0.99
    ]
).T

sold_numeric_summary = sold_numeric_summary[
    [
        "min",
        "max",
        "mean",
        "50%",
        "1%",
        "5%",
        "25%",
        "75%",
        "95%",
        "99%"
    ]
].rename(columns={
    "min": "Min",
    "max": "Max",
    "mean": "Mean",
    "50%": "Median"
}).round(2)


listing_numeric_summary = listing_numeric.describe(
    percentiles=[
        0.01,
        0.05,
        0.25,
        0.50,
        0.75,
        0.95,
        0.99
    ]
).T

listing_numeric_summary = listing_numeric_summary[
    [
        "min",
        "max",
        "mean",
        "50%",
        "1%",
        "5%",
        "25%",
        "75%",
        "95%",
        "99%"
    ]
].rename(columns={
    "min": "Min",
    "max": "Max",
    "mean": "Mean",
    "50%": "Median"
}).round(2)


print("\n" + "-" * 110)
print("SOLD NUMERIC DISTRIBUTION SUMMARY")
print("-" * 110)
print(sold_numeric_summary.to_string())

print("\n" + "-" * 110)
print("LISTING NUMERIC DISTRIBUTION SUMMARY")
print("-" * 110)
print(listing_numeric_summary.to_string())


# --------------------------------------------------
# SAVE FILTERED DATASETS
# --------------------------------------------------

sold_clean.to_csv(
    DATA_DIR / "sold_clean.csv",
    index=False
)

listing_clean.to_csv(
    DATA_DIR / "listing_clean.csv",
    index=False
)

print("\n" + "-" * 60)
print("SAVED FILES")
print("-" * 60)
print(DATA_DIR / "sold_clean.csv")
print(DATA_DIR / "listing_clean.csv")
