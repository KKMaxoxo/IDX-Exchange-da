"""
Week 4: Data Cleaning and Preparation

This script:
- Converts date fields to datetime.
- Converts required fields to numeric.
- Removes invalid numeric rows.
- Adds date and geographic quality flags.
- Standardizes ZIP codes and keeps valid California ZIP-code rows.
- Removes unnecessary columns.
- Saves cleaned sold and listing datasets.
"""

from pathlib import Path
import pandas as pd


DATA_DIR = Path("/Users/kmaxx/Desktop/IDX-da/idx_data")

SOLD_INPUT = DATA_DIR / "sold_with_rates.csv"
LISTING_INPUT = DATA_DIR / "listing_with_rates.csv"

SOLD_OUTPUT = DATA_DIR / "cleaned_sold.csv"
LISTING_OUTPUT = DATA_DIR / "cleaned_listing.csv"


DATE_COLUMNS = [
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "ContractStatusChangeDate",
]

SOLD_NUMERIC_COLUMNS = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "DaysOnMarket",
    "BedroomsTotal",
    "BathroomsTotalInteger",
]

LISTING_NUMERIC_COLUMNS = [
    "ListPrice",
    "OriginalListPrice",
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket",
    "BedroomsTotal",
    "BathroomsTotalInteger",
]

SOLD_COLUMNS_TO_REMOVE = [
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
    "BuyerAgencyCompensationType",
]

LISTING_COLUMNS_TO_REMOVE = [
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
    "BuyerAgencyCompensationType",
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
    "UnparsedAddress.1",
]


def load_dataset(file_path):
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    df = pd.read_csv(file_path, low_memory=False)
    df.columns = df.columns.str.strip()
    return df


def convert_date_fields(df):
    data = df.copy()
    existing_columns = [column for column in DATE_COLUMNS if column in data.columns]
    data[existing_columns] = data[existing_columns].apply(pd.to_datetime, errors="coerce")
    return data


def convert_numeric_fields(df, numeric_columns):
    data = df.copy()
    existing_columns = [column for column in numeric_columns if column in data.columns]
    data[existing_columns] = data[existing_columns].apply(pd.to_numeric, errors="coerce")
    return data


def remove_invalid_numeric_values(df, price_column, dataset_name):
    required_columns = [
        price_column,
        "LivingArea",
        "DaysOnMarket",
        "BedroomsTotal",
        "BathroomsTotalInteger",
    ]

    missing_columns = [column for column in required_columns if column not in df.columns]

    if missing_columns:
        raise KeyError(f"{dataset_name} is missing required columns: {missing_columns}")

    valid_mask = (
        df[price_column].gt(0)
        & df["LivingArea"].gt(0)
        & df["DaysOnMarket"].ge(0)
        & df["BedroomsTotal"].ge(0)
        & df["BathroomsTotalInteger"].ge(0)
    )

    cleaned_df = df.loc[valid_mask].copy()

    print(f"\n{dataset_name.upper()} NUMERIC CLEANING")
    print(f"Rows before cleaning: {len(df):,}")
    print(f"Rows after cleaning:  {len(cleaned_df):,}")
    print(f"Rows removed:         {len(df) - len(cleaned_df):,}")

    return cleaned_df


def add_date_consistency_flags(df):
    data = df.copy()

    for column in DATE_COLUMNS:
        if column not in data.columns:
            data[column] = pd.NaT

    data["listing_after_close_flag"] = data["ListingContractDate"] > data["CloseDate"]
    data["purchase_after_close_flag"] = data["PurchaseContractDate"] > data["CloseDate"]
    data["negative_timeline_flag"] = (
        (data["ListingContractDate"] > data["PurchaseContractDate"])
        | (data["PurchaseContractDate"] > data["CloseDate"])
        | (data["ListingContractDate"] > data["CloseDate"])
    )

    return data


def add_geographic_flags(df):
    data = df.copy()

    for column in ["Latitude", "Longitude"]:
        if column not in data.columns:
            data[column] = pd.NA

    data[["Latitude", "Longitude"]] = data[["Latitude", "Longitude"]].apply(
        pd.to_numeric,
        errors="coerce",
    )

    data["missing_coordinates_flag"] = data["Latitude"].isna() | data["Longitude"].isna()
    data["zero_coordinates_flag"] = data["Latitude"].eq(0) | data["Longitude"].eq(0)
    data["positive_longitude_flag"] = data["Longitude"].gt(0)
    data["implausible_coordinates_flag"] = (
        data["Latitude"].lt(32)
        | data["Latitude"].gt(42)
        | data["Longitude"].lt(-125)
        | data["Longitude"].gt(-114)
    )

    return data


def clean_and_filter_postal_codes(df, dataset_name):
    if "PostalCode" not in df.columns:
        raise KeyError(f"'PostalCode' is missing from the {dataset_name} dataset.")

    data = df.copy()

    data["PostalCode"] = (
        data["PostalCode"]
        .astype("string")
        .str.strip()
        .str.split("-")
        .str[0]
        .str.zfill(5)
    )

    postal_numeric = pd.to_numeric(data["PostalCode"], errors="coerce")
    valid_mask = postal_numeric.between(90001, 96162)

    outside_ca_columns = [column for column in ["PostalCode", "City"] if column in data.columns]
    outside_ca = data.loc[~valid_mask, outside_ca_columns].copy()

    cleaned_df = data.loc[valid_mask].copy()
    cleaned_df.reset_index(drop=True, inplace=True)

    print(f"\n{dataset_name.upper()} POSTAL-CODE CLEANING")
    print(f"Rows before ZIP filter: {len(data):,}")
    print(f"Rows after ZIP filter:  {len(cleaned_df):,}")
    print(f"Rows removed:           {len(data) - len(cleaned_df):,}")

    outside_ca.to_csv(DATA_DIR / f"{dataset_name}_outside_california_zip.csv", index=False)

    return cleaned_df


def process_sold_data():
    sold_df = load_dataset(SOLD_INPUT)
    sold_df = convert_date_fields(sold_df)
    sold_df = convert_numeric_fields(sold_df, SOLD_NUMERIC_COLUMNS)
    sold_df = remove_invalid_numeric_values(sold_df, "ClosePrice", "sold")
    sold_df = add_date_consistency_flags(sold_df)
    sold_df = add_geographic_flags(sold_df)
    sold_df = clean_and_filter_postal_codes(sold_df, "sold")
    sold_df = sold_df.drop(columns=SOLD_COLUMNS_TO_REMOVE, errors="ignore")
    sold_df.to_csv(SOLD_OUTPUT, index=False)

    print(f"\nFinal sold shape: {sold_df.shape}")
    print(f"Saved sold data: {SOLD_OUTPUT}")

    return sold_df


def process_listing_data():
    listing_df = load_dataset(LISTING_INPUT)
    listing_df = convert_date_fields(listing_df)
    listing_df = convert_numeric_fields(listing_df, LISTING_NUMERIC_COLUMNS)
    listing_df = remove_invalid_numeric_values(listing_df, "ListPrice", "listing")
    listing_df = add_date_consistency_flags(listing_df)
    listing_df = add_geographic_flags(listing_df)
    listing_df = clean_and_filter_postal_codes(listing_df, "listing")
    listing_df = listing_df.drop(columns=LISTING_COLUMNS_TO_REMOVE, errors="ignore")
    listing_df.to_csv(LISTING_OUTPUT, index=False)

    print(f"\nFinal listing shape: {listing_df.shape}")
    print(f"Saved listing data: {LISTING_OUTPUT}")

    return listing_df


def main():
    process_sold_data()
    process_listing_data()


if __name__ == "__main__":
    main()
