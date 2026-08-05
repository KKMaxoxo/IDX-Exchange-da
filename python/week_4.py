"""
Week 4: Clean and prepare the sold and listing datasets.

Transformations performed:
1. Strip whitespace from column names so columns are referenced consistently.
2. Convert date fields to datetime so timeline checks can be performed.
3. Convert required numeric fields to numeric and coerce invalid text to missing.
4. Remove rows with invalid required numeric values.
5. Add date-consistency flags rather than silently deleting timeline problems.
6. Convert coordinates to numeric and add geographic-quality flags.
7. Standardize ZIP codes and keep valid California ZIP-code rows.
8. Remove unnecessary agent, compensation, and duplicate columns.
9. Save cleaned, analysis-ready sold and listing CSV files.
"""

from pathlib import Path
from datetime import datetime
import re
import pandas as pd
import os

DATA_DIR = Path("/Users/kmaxx/Desktop/IDX-da/idx_final_data")

sold_df = pd.read_csv(DATA_DIR / "sold_with_rates.csv", low_memory= False)
listing_df = pd.read_csv(DATA_DIR / "listing_with_rates.csv", low_memory= False)

def convert_date_fields(df):
    date_cols = [
        "CloseDate",
        "PurchaseContractDate",
        "ListingContractDate",
        "ContractStatusChangeDate"
    ]

    df = df.copy()
    df.columns = df.columns.str.strip()

    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    return df

sold_df = convert_date_fields(sold_df)
listing_df = convert_date_fields(listing_df)

def sold_remove_invalid_numeric_values(df):
    data = df.copy()

    numeric_cols = [
        "ClosePrice",
        "LivingArea",
        "DaysOnMarket",
        "BedroomsTotal",
        "BathroomsTotalInteger"
    ]

    for col in numeric_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    valid_mask = (
        (data["ClosePrice"] > 0) &
        (data["LivingArea"] > 0) &
        (data["DaysOnMarket"] >= 0) &
        (data["BedroomsTotal"] >= 0) &
        (data["BathroomsTotalInteger"] >= 0)
    )

    cleaned_df = data[valid_mask].copy()

    print(f"Rows before cleaning: {len(data):,}")
    print(f"Rows after cleaning:  {len(cleaned_df):,}")
    print(f"Rows removed:         {len(data) - len(cleaned_df):,}")

    return cleaned_df

sold_df = sold_remove_invalid_numeric_values(sold_df)


def list_remove_invalid_numeric_values(df):
    data = df.copy()

    numeric_cols = [
        "ClosePrice",
        "LivingArea",
        "DaysOnMarket",
        "BedroomsTotal",
        "BathroomsTotalInteger"
    ]

    for col in numeric_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    valid_mask = (
        (data["ListPrice"] > 0) &
        (data["LivingArea"] > 0) &
        (data["DaysOnMarket"] >= 0) &
        (data["BedroomsTotal"] >= 0) &
        (data["BathroomsTotalInteger"] >= 0)
    )

    cleaned_df = data[valid_mask].copy()

    print(f"Rows before cleaning: {len(data):,}")
    print(f"Rows after cleaning:  {len(cleaned_df):,}")
    print(f"Rows removed:         {len(data) - len(cleaned_df):,}")

    return cleaned_df

def list_remove_invalid_numeric_values(df):
    data = df.copy()

    numeric_cols = [
        "ClosePrice",
        "LivingArea",
        "DaysOnMarket",
        "BedroomsTotal",
        "BathroomsTotalInteger"
    ]

    for col in numeric_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    valid_mask = (
        (data["ListPrice"] > 0) &
        (data["LivingArea"] > 0) &
        (data["DaysOnMarket"] >= 0) &
        (data["BedroomsTotal"] >= 0) &
        (data["BathroomsTotalInteger"] >= 0)
    )

    cleaned_df = data[valid_mask].copy()

    print(f"Rows before cleaning: {len(data):,}")
    print(f"Rows after cleaning:  {len(cleaned_df):,}")
    print(f"Rows removed:         {len(data) - len(cleaned_df):,}")

    return cleaned_df

listing_df = list_remove_invalid_numeric_values(listing_df)

def add_date_consistency_flags(df):
    data = df.copy()

    date_cols = [
        "ListingContractDate",
        "PurchaseContractDate",
        "CloseDate",
        "ContractStatusChangeDate"
    ]

    for col in date_cols:
        if col in data.columns:
            data[col] = pd.to_datetime(data[col], errors="coerce")

    data["listing_after_close_flag"] = (
        data["ListingContractDate"] > data["CloseDate"]
    )

    data["purchase_after_close_flag"] = (
        data["PurchaseContractDate"] > data["CloseDate"]
    )

    data["negative_timeline_flag"] = (
        (data["ListingContractDate"] > data["PurchaseContractDate"]) |
        (data["PurchaseContractDate"] > data["CloseDate"]) |
        (data["ListingContractDate"] > data["CloseDate"])
    )

    return data

sold_df = add_date_consistency_flags(sold_df)
listing_df = add_date_consistency_flags(listing_df)

def add_geographic_flags(df):
    data = df.copy()

    data["Latitude"] = pd.to_numeric(data["Latitude"], errors="coerce")
    data["Longitude"] = pd.to_numeric(data["Longitude"], errors="coerce")

    # Missing coordinates
    data["missing_coordinates_flag"] = (
        data["Latitude"].isna() | data["Longitude"].isna()
    )

    # Sentinel null values
    data["zero_coordinates_flag"] = (
        (data["Latitude"] == 0) | (data["Longitude"] == 0)
    )

    # California longitudes should be negative
    data["positive_longitude_flag"] = (
        data["Longitude"] > 0
    )

    # Rough California coordinate bounds
    data["implausible_coordinates_flag"] = (
        (data["Latitude"] < 32) |
        (data["Latitude"] > 42) |
        (data["Longitude"] < -125) |
        (data["Longitude"] > -114)
    )

    return data

sold_df = add_date_consistency_flags(sold_df)
listing_df = add_date_consistency_flags(listing_df)

sold_postal_city = sold_df[["PostalCode", "City"]]

sold_postal = pd.to_numeric(
    sold_df["PostalCode"],
    errors="coerce"
)

outside_ca = sold_df.loc[~sold_postal.between(90001, 96162)].copy()
outside_ca[["PostalCode", "City"]].head()

# Remove number behind dash
sold_df["PostalCode"] = (
    sold_df["PostalCode"]
    .astype("string")
    .str.strip()
    .str.split("-").str[0]  
    .str.zfill(5)
)

sold_postal = pd.to_numeric(
    sold_df["PostalCode"],
    errors="coerce"
)
outside_ca = sold_df.loc[~sold_postal.between(90001, 96162)].copy()
outside_ca[["PostalCode", "City"]].head()

# Keep only valid California ZIP-code rows
sold_df = sold_df.loc[
    sold_postal.between(90001, 96162)
].copy()

sold_df.reset_index(drop=True, inplace=True)

listing_postal_city =listing_df[["PostalCode", "City"]]

listing_postal = pd.to_numeric(
    listing_df["PostalCode"],
    errors="coerce"
)
list_outside_ca = listing_df.loc[~listing_postal.between(90001, 96162)].copy()
list_outside_ca[["PostalCode", "City"]].head()

# Remove number after dash
listing_df["PostalCode"] = (
    listing_df["PostalCode"]
    .astype("string")
    .str.strip()
    .str.split("-").str[0]  
    .str.zfill(5)
)

listing_postal = pd.to_numeric(
    listing_df["PostalCode"],
    errors="coerce"
)
listing_outside_ca = listing_df.loc[~listing_postal.between(90001, 96162)].copy()
listing_outside_ca[["PostalCode", "City"]].head()

# Keep only valid California ZIP-code rows
listing_df = listing_df.loc[
    listing_postal.between(90001, 96162)
].copy()

listing_df.reset_index(drop=True, inplace=True)
sold_core_variables = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "CloseDate",
    "ListingContractDate",
    "PurchaseContractDate",
    "PropertySubType",
    "City",
    "CountyOrParish",
    "PostalCode",
    "Latitude",
    "Longitude",
    "YearBuilt",
    "LotSizeSquareFeet",
    "GarageSpaces",
    "ParkingTotal",
    "PoolPrivateYN",
    "rate_30yr_fixed"
]
sold_secondary_variables = [
    "PropertyType",
    "MLSAreaMajor",
    "SubdivisionName",
    "AssociationFee",
    "AssociationFeeFrequency",
    "NewConstructionYN",
    "AttachedGarageYN",
    "FireplaceYN",
    "ViewYN",
    "MainLevelBedrooms",
    "Stories",
    "Levels",
    "Flooring",
    "LotSizeAcres",
    "HighSchoolDistrict",
    "ElementarySchool",
    "MiddleOrJuniorSchool",
    "HighSchool",
    "MlsStatus",
    "StateOrProvince",
    "OriginatingSystemName",
    "OriginatingSystemSubName"
    "ListOfficeName",
    "BuyerOfficeName"
]
sold_to_remove = [
    "ListAgentFullName",
    "ListAgentFirstName",
    "ListAgentLastName",
    "ListAgentEmail",
    "ListAgentAOR",
    "CoListAgentFirstName",
    "CoListAgentLastName",
    "CoListOfficeName",
    "BuyerAgentMlsId",
    "BuyerAgentFirstName",
    "BuyerAgentLastName",
    "BuyerAgentAOR",
    "BuyerOfficeAOR",
    "BuyerAgencyCompensation",
    "BuyerAgencyCompensationType"
]
sold_df = sold_df.drop(
    columns=sold_to_remove,
    errors="ignore"
)

list_core_variables = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "CloseDate",
    "ListingContractDate",
    "PurchaseContractDate",
    "PropertySubType",
    "City",
    "CountyOrParish",
    "PostalCode",
    "Latitude",
    "Longitude",
    "YearBuilt",
    "LotSizeSquareFeet",
    "GarageSpaces",
    "ParkingTotal",
    "rate_30yr_fixed"
]
list_secondary_variables = [
    "PropertyType",
    "MLSAreaMajor",
    "SubdivisionName",
    "AssociationFee",
    "AssociationFeeFrequency",
    "NewConstructionYN",
    "AttachedGarageYN",
    "FireplaceYN",
    "MainLevelBedrooms",
    "Stories",
    "Levels",
    "LotSizeAcres",
    "LotSizeArea",
    "HighSchoolDistrict",
    "ElementarySchool",
    "MiddleOrJuniorSchool",
    "HighSchool",
    "MlsStatus",
    "StateOrProvince",
    "ContractStatusChangeDate",
    "UnparsedAddress"
    "ListOfficeName"
    "BuyerOfficeName"
]
identifier_variables = [
    "ListingKey",
    "ListingKeyNumeric",
    "ListingId",
    "StreetNumberNumeric"
]
list_to_remove = [
    "ListAgentFullName",
    "ListAgentFirstName",
    "ListAgentLastName",
    "ListAgentEmail",
    "CoListAgentFirstName",
    "CoListAgentLastName",
    "CoListOfficeName",
    "BuyerAgentMlsId",
    "BuyerAgentFirstName",
    "BuyerAgentLastName",
    "BuyerOfficeAOR",
    "BuyerAgencyCompensation",
    "BuyerAgencyCompensationType"
    "PropertyType.1",
    "ListAgentFirstName.1",
    "DaysOnMarket.1",
    "LivingArea.1",
    "Longitude.1",
    "Latitude.1",
    "ListPrice.1",
    "ListAgentLastName.1",
    "CloseDate.1",
    "BuyerOfficeName.1",
    "UnparsedAddress.1"
]

listing_df = listing_df.drop(
    columns=list_to_remove,
    errors="ignore"
)

sold_df.shape

listing_df.shape

sold_df.to_csv(DATA_DIR / "cleaned_sold.csv", index = False)
listing_df.to_csv(DATA_DIR / "cleaned_listing.csv", index = False)