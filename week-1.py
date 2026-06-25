import pandas as pd
from pathlib import Path

DATA_DIR = Path("Desktop/IDX-da/idx_data")

START_MONTH = "202401"
END_MONTH = "202605"


def month_range(start_month, end_month):
    months = []

    year = int(start_month[:4])
    month = int(start_month[4:])

    end_year = int(end_month[:4])
    end_month_num = int(end_month[4:])

    while (year, month) <= (end_year, end_month_num):
        months.append(f"{year}{month:02d}")

        month += 1
        if month == 13:
            month = 1
            year += 1

    return months


def combine_monthly_files(prefix, dataset_name, start_month, end_month):
    all_dfs = []
    months = month_range(start_month, end_month)

    for month in months:
        file_path = DATA_DIR / f"{prefix}{month}.csv"

        if file_path.exists():
            print(f"Loading {file_path}")
            df = pd.read_csv(file_path)

            # Track which monthly file each row came from
            df["SourceMonth"] = month

            all_dfs.append(df)
        else:
            print(f"Missing file: {file_path}")

    if not all_dfs:
        print(f"No files found for {dataset_name}")
        return

    combined = pd.concat(all_dfs, ignore_index=True)

    # Basic cleaning
    combined = combined.dropna(how="all")

    if "ListingKey" in combined.columns:
        combined = combined.drop_duplicates(subset=["ListingKey"], keep="last")

    date_columns = [
        "CloseDate",
        "ListingContractDate",
        "PurchaseContractDate",
        "ContractStatusChangeDate",
    ]

    for col in date_columns:
        if col in combined.columns:
            combined[col] = pd.to_datetime(combined[col], errors="coerce")

    output_name = f"{dataset_name}_{start_month}_{end_month}.csv"
    combined.to_csv(output_name, index=False)

    print(f"Saved {len(combined)} rows to {output_name}")


combine_monthly_files(
    prefix="CRMLSSold",
    dataset_name="CombinedSoldTransactions",
    start_month=START_MONTH,
    end_month=END_MONTH
)

combine_monthly_files(
    prefix="CRMLSListing",
    dataset_name="CombinedListingData",
    start_month=START_MONTH,
    end_month=END_MONTH
)