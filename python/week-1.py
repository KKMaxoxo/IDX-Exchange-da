# =============================================================================
# 1. IMPORTS
# =============================================================================

from pathlib import Path
from datetime import datetime
import re
import pandas as pd


# =============================================================================
# 2. SETTINGS
# =============================================================================

# Folder where your monthly MLS CSV files are stored
DATA_DIR = Path("/Users/kmaxx/Desktop/IDX-da/idx_data")

# Folder where output CSVs will be saved
OUTPUT_DIR = Path("combined_output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Start month: January 2024
START_MONTH = "202401"

# Use None to automatically use the most recently completed calendar month
# Example: if today is June 2026, END_MONTH becomes "202605"
END_MONTH = '202605'
SOLD_PREFIX = "CRMLSSold"
LISTING_PREFIX = "CRMLSListing"


# =============================================================================
# 3. MONTH HELPERS
# =============================================================================

def get_most_recent_completed_month():
    today = datetime.today()

    if today.month == 1:
        year = today.year - 1
        month = 12
    else:
        year = today.year
        month = today.month - 1

    return f"{year}{month:02d}"


def get_end_month():
    if END_MONTH is not None:
        return END_MONTH

    return get_most_recent_completed_month()


# =============================================================================
# 4. FILE HELPERS
# =============================================================================

def get_month_from_filename(file_name, prefix):
    """
    Extract YYYYMM from file names like:
        CRMLSSold202401.csv
        CRMLSListing202403.csv
    """
    match = re.search(rf"{prefix}(\d{{6}})", file_name)

    if match:
        return match.group(1)

    return None


def get_files_for_dataset(prefix, start_month, end_month):
    """
    Get all files for one dataset type.

    Important:
        Files with "filled" in the filename are skipped.
    """
    files = []

    for file_path in DATA_DIR.glob(f"{prefix}*.csv"):
        file_name_lower = file_path.name.lower()

        # Skip filled files
        if "filled" in file_name_lower:
            continue

        month = get_month_from_filename(file_path.name, prefix)

        if month is None:
            continue

        if start_month <= month <= end_month:
            files.append((month, file_path))

    files.sort(key=lambda x: x[0])

    return files


# =============================================================================
# 5. COMBINE, FILTER, AND SAVE FUNCTION
# =============================================================================

def combine_filter_save(prefix, dataset_name, start_month, end_month):
    print("\n" + "=" * 80)
    print(f"PROCESSING {dataset_name}")
    print("=" * 80)

    files = get_files_for_dataset(prefix, start_month, end_month)

    if not files:
        raise FileNotFoundError(f"No files found for {dataset_name}")

    dataframes = []

    # -------------------------------------------------------------------------
    # ROW COUNTS BEFORE CONCATENATION
    # CombinedSoldTransactions: 495,671 rows
    # CombinedListingData: 893,594 rows
    # -------------------------------------------------------------------------

    for month, file_path in files:
        df = pd.read_csv(file_path, low_memory=False)

        # Add source tracking columns
        df["SourceMonth"] = month
        df["SourceFile"] = file_path.name

        print(f"Before concatenation | {file_path.name}: {len(df):,} rows")

        dataframes.append(df)

    total_rows_before_concat = sum(len(df) for df in dataframes)

    print(f"\nBefore concatenation total | {dataset_name}: {total_rows_before_concat:,} rows")

    # -------------------------------------------------------------------------
    # CONCATENATE MONTHLY FILES
    # -------------------------------------------------------------------------

    combined_df = pd.concat(dataframes, ignore_index=True)

    # -------------------------------------------------------------------------
    # ROW COUNT AFTER CONCATENATION
    # CombinedSoldTransactions: 495,671 rows
    # CombinedListingData: 893,594 rows
    # -------------------------------------------------------------------------

    rows_after_concat = len(combined_df)

    print(f"After concatenation        | {dataset_name}: {rows_after_concat:,} rows")

    if rows_after_concat == total_rows_before_concat:
        print("Concatenation check        | PASSED")
    else:
        print("Concatenation check        | WARNING: row count mismatch")

    # -------------------------------------------------------------------------
    # ROW COUNT BEFORE RESIDENTIAL FILTER
    # CombinedSoldTransactions: 495,671 rows
    # CombinedListingData: 893,594 rows
    # -------------------------------------------------------------------------

    rows_before_filter = len(combined_df)

    print(f"\nBefore Residential filter  | {dataset_name}: {rows_before_filter:,} rows")

    # -------------------------------------------------------------------------
    # FILTER TO PROPERTYTYPE == RESIDENTIAL
    # -------------------------------------------------------------------------

    if "PropertyType" not in combined_df.columns:
        raise ValueError(f"PropertyType column not found in {dataset_name}")

    residential_df = combined_df[
        combined_df["PropertyType"].astype(str).str.strip() == "Residential"
    ].copy()

    # -------------------------------------------------------------------------
    # ROW COUNT AFTER RESIDENTIAL FILTER 
    # CombinedSoldTransactions: 333,598 rows
    # CombinedListingData: 567,549 rows
    # -------------------------------------------------------------------------

    rows_after_filter = len(residential_df)

    print(f"After Residential filter   | {dataset_name}: {rows_after_filter:,} rows")
    print(f"Rows removed by filter     | {dataset_name}: {rows_before_filter - rows_after_filter:,} rows")

    # -------------------------------------------------------------------------
    # SAVE FILTERED CSV
    # -------------------------------------------------------------------------

    output_path = OUTPUT_DIR / f"{dataset_name}_Residential_{start_month}_{end_month}.csv"

    residential_df.to_csv(output_path, index=False)

    print(f"\nSaved file: {output_path}")

    return residential_df


# =============================================================================
# 6. RUN SCRIPT
# =============================================================================

def main():
    end_month = get_end_month()

    print("=" * 80)
    print("MLS COMBINE + RESIDENTIAL FILTER")
    print("=" * 80)
    print(f"Data folder: {DATA_DIR.resolve()}")
    print(f"Output folder: {OUTPUT_DIR.resolve()}")
    print(f"Month range: {START_MONTH} through {end_month}")
    print('Skipping files with "filled" in the filename')
    print("=" * 80)

    # -------------------------------------------------------------------------
    # COMBINED SOLD TRANSACTIONS DATASET
    # 
    # -------------------------------------------------------------------------

    sold_df = combine_filter_save(
        prefix=SOLD_PREFIX,
        dataset_name="CombinedSoldTransactions",
        start_month=START_MONTH,
        end_month=end_month
    )

    # -------------------------------------------------------------------------
    # COMBINED LISTING DATA DATASET
    # -------------------------------------------------------------------------

    listing_df = combine_filter_save(
        prefix=LISTING_PREFIX,
        dataset_name="CombinedListingData",
        start_month=START_MONTH,
        end_month=end_month
    )

    # -------------------------------------------------------------------------
    # FINAL ROW COUNTS
    # -------------------------------------------------------------------------

    print("\n" + "=" * 80)
    print("FINAL OUTPUT ROW COUNTS")
    print("=" * 80)
    print(f"Combined sold Residential rows: {len(sold_df):,}")
    print(f"Combined listing Residential rows: {len(listing_df):,}")
    print("Done.")


if __name__ == "__main__":
    main()