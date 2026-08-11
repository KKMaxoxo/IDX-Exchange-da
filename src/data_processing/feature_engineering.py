"""
Week 6: Create the required engineered metrics, display a sample output table,
create a segmented county summary, and save the featured datasets.
"""

from pathlib import Path
from datetime import datetime
import re
import pandas as pd
import geopandas as gpd

import os

DATA_DIR = Path("/Users/kmaxx/Desktop/IDX-da/idx_final_data")

sold_df = pd.read_csv(DATA_DIR / "cleaned_sold.csv", low_memory= False)
listing_df = pd.read_csv(DATA_DIR / "cleaned_listing.csv", low_memory= False)

date_columns = [
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate"
]

numeric_columns = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "DaysOnMarket"
]

for df in [sold_df, listing_df]:
    existing_dates = [col for col in date_columns if col in df.columns]
    existing_numeric = [col for col in numeric_columns if col in df.columns]

    df[existing_dates] = df[existing_dates].apply(pd.to_datetime, errors="coerce")
    df[existing_numeric] = df[existing_numeric].apply(pd.to_numeric, errors="coerce")

    # Close price compared with original list price
sold_df["PriceRatio"] = sold_df["ClosePrice"] / sold_df["OriginalListPrice"]

# Price per square foot
sold_df["PricePerSqFt"] = sold_df["ClosePrice"] / sold_df["LivingArea"]

# Date-based variables
sold_df["Year"] = sold_df["CloseDate"].dt.year
sold_df["Month"] = sold_df["CloseDate"].dt.month
sold_df["YrMo"] = sold_df["CloseDate"].dt.to_period("M")

# Days from listing to accepted contract
sold_df["ListingToContractDays"] = (sold_df["PurchaseContractDate"] - sold_df["ListingContractDate"]).dt.days

# Days from accepted contract to closing
sold_df["ContractToCloseDays"] = (sold_df["CloseDate"] - sold_df["PurchaseContractDate"]).dt.days

metric_columns = [
    "PriceRatio",
    "PricePerSqFt",
    "ListingToContractDays",
    "ContractToCloseDays"
]

missing_summary = sold_df[metric_columns].isna().sum().to_frame("missing_count")
missing_summary["missing_pct"] = (missing_summary["missing_count"] / len(sold_df) * 100).round(2)



districts = gpd.read_file(
    DATA_DIR / "DistrictAreas2526.geojson"
)

print(districts.shape)
print(districts.crs)
print(districts.columns.tolist())

district_type_summary = districts["DistrictType"].value_counts(dropna=False).rename_axis("DistrictType").reset_index(name="Count")

district_type_summary["Percentage"] = (district_type_summary["Count"] / district_type_summary["Count"].sum() * 100).round(2)


unified_districts = districts.loc[districts["DistrictType"].astype("string").str.strip().str.casefold().eq("unified")].copy()
unified_districts = unified_districts[["DistrictName", "geometry"]].copy()

print("Unified districts:", len(unified_districts))
unified_districts.head()

coordinate_columns = [
    "Latitude",
    "Longitude"
]

sold_df[coordinate_columns] = sold_df[coordinate_columns].apply(pd.to_numeric, errors="coerce")

valid_coordinates = sold_df[coordinate_columns].notna().all(axis=1)

sold_points = gpd.GeoDataFrame(
    sold_df.loc[valid_coordinates].copy(),
    geometry=gpd.points_from_xy(
        sold_df.loc[valid_coordinates, "Longitude"],
        sold_df.loc[valid_coordinates, "Latitude"]
    ),
    crs="EPSG:4326"
)

sold_points[coordinate_columns + ["geometry"]].head()

join_columns = [
    "DistrictName",
    "geometry"
]

preview_columns = [
    "Latitude",
    "Longitude",
    "DistrictName"
]

# Match the coordinate reference systems
sold_points = sold_points.to_crs(unified_districts.crs)

# Match each property point to its unified school district
sold_joined = gpd.sjoin(sold_points,unified_districts[join_columns],how="left",predicate="within")

sold_joined[preview_columns].head()

# Create one district result for each original row
district_lookup = sold_joined.groupby(level=0)["DistrictName"].first()

# Add the district name to the original sold dataset
sold_df["DistrictName"] = sold_df.index.map(district_lookup)

preview_columns = [
    "UnparsedAddress",
    "City",
    "Latitude",
    "Longitude",
    "DistrictName"
]


print(
    "Properties without a unified district:",
    sold_df["DistrictName"].isna().sum()
)

print(
    "Missing percentage:",
    round(sold_df["DistrictName"].isna().mean() * 100, 2),
    "%"
)

coordinate_columns = [
    "Latitude",
    "Longitude"
]

listing_df[coordinate_columns] = listing_df[coordinate_columns].apply(pd.to_numeric, errors="coerce")

valid_coordinates = listing_df[coordinate_columns].notna().all(axis=1)

listing_points = gpd.GeoDataFrame(
    listing_df.loc[valid_coordinates].copy(),
    geometry=gpd.points_from_xy(
        listing_df.loc[valid_coordinates, "Longitude"],
        listing_df.loc[valid_coordinates, "Latitude"]
    ),
    crs="EPSG:4326"
)

listing_points = listing_points.to_crs(unified_districts.crs)

listing_joined = gpd.sjoin(
    listing_points,
    unified_districts[
        [
            "DistrictName",
            "geometry"
        ]
    ],
    how="left",
    predicate="within"
)

district_lookup = listing_joined.groupby(level=0)["DistrictName"].first()
listing_df["DistrictName"] = listing_df.index.map(district_lookup)

preview_columns = [
    "UnparsedAddress",
    "City",
    "Latitude",
    "Longitude",
    "DistrictName"
]


print("Matched:", listing_df["DistrictName"].notna().sum())
print("No district match:", listing_df["DistrictName"].isna().sum())

sold_df.to_csv(DATA_DIR / "featured_sold.csv", index = False)
listing_df.to_csv(DATA_DIR / "featured_listing.csv", index = False)


def create_segment_summary(df, group_columns):
    required_metrics = [
        "ClosePrice",
        "PriceRatio",
        "PricePerSqFt",
        "DaysOnMarket",
        "ListingToContractDays",
        "ContractToCloseDays"
    ]

    data = df.copy()

    for col in required_metrics:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    count_column = "ListingKey" if "ListingKey" in data.columns else "ClosePrice"

    summary = data.groupby(
        group_columns,
        dropna=False,
        observed=True
    ).agg(
        ListingCount=(count_column, "nunique"),
        AverageClosePrice=("ClosePrice", "mean"),
        AveragePriceRatio=("PriceRatio", "mean"),
        AveragePricePerSqFt=("PricePerSqFt", "mean"),
        AverageDaysOnMarket=("DaysOnMarket", "mean"),
        AverageListingToContractDays=("ListingToContractDays", "mean"),
        AverageContractToCloseDays=("ContractToCloseDays", "mean")
    ).reset_index()

    mean_columns = [
        col for col in summary.select_dtypes("number").columns
        if col != "ListingCount"
    ]

    summary[mean_columns] = summary[mean_columns].round(2)

    return summary.sort_values(["ListingCount", "AverageClosePrice"], ascending=[False, False]).reset_index(drop=True)

print(create_segment_summary(sold_df,["CountyOrParish","PropertySubType"]))


