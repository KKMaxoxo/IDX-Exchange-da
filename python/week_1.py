"""
Combine CRMLS monthly sold and listing CSV files from January 2024 through
the most recently completed calendar month, keep Residential properties only,
and save two combined CSV files.
"""

from pathlib import Path
import re
import pandas as pd


# Update this path if the monthly CSV files are stored somewhere else.
DATA_DIR = Path("/Users/kmaxx/Desktop/IDX-da/idx_data")

SOLD_PREFIX = "CRMLSSold"
LISTING_PREFIX = "CRMLSListing"

START_MONTH = pd.Period("2024-01", freq="M")
END_MONTH = pd.Timestamp.today().to_period("M") - 1


def find_monthly_files(prefix):
    """Return one CSV file per month within the required date range."""
    monthly_candidates = {}

    for file_path in DATA_DIR.glob("*.csv"):
        if not file_path.name.startswith(prefix):
            continue

        match = re.search(r"(20\d{2})(0[1-9]|1[0-2])", file_path.stem)
        if match is None:
            continue

        file_month = pd.Period(f"{match.group(1)}-{match.group(2)}", freq="M")

        if START_MONTH <= file_month <= END_MONTH:
            monthly_candidates.setdefault(file_month, []).append(file_path)

    selected_files = []

    for month in sorted(monthly_candidates):
        candidates = monthly_candidates[month]

        if len(candidates) == 1:
            selected_files.append(candidates[0])
            continue

        filled_candidates = [
            file_path
            for file_path in candidates
            if "filled" in file_path.stem.lower()
        ]

        if len(filled_candidates) == 1:
            selected_files.append(filled_candidates[0])
        else:
            names = ", ".join(file_path.name for file_path in candidates)
            raise ValueError(f"Multiple files found for {month}: {names}")

    if not selected_files:
        raise FileNotFoundError(
            f"No {prefix} monthly CSV files were found from "
            f"{START_MONTH} through {END_MONTH} in {DATA_DIR}."
        )

    expected_months = set(pd.period_range(START_MONTH, END_MONTH, freq="M"))
    found_months = {
        pd.Period(
            f"{re.search(r'(20\d{2})(0[1-9]|1[0-2])', file_path.stem).group(1)}-"
            f"{re.search(r'(20\d{2})(0[1-9]|1[0-2])', file_path.stem).group(2)}",
            freq="M"
        )
        for file_path in selected_files
    }
    missing_months = sorted(expected_months - found_months)

    if missing_months:
        print(
            f"Warning: missing {prefix} files for: "
            + ", ".join(str(month) for month in missing_months)
        )

    return selected_files


def combine_and_filter(prefix, dataset_name):
    """Concatenate monthly files and retain Residential records only."""
    files = find_monthly_files(prefix)
    frames = []
    total_before_concat = 0

    print(f"\n{dataset_name.upper()} FILES")
    print(f"Date range: {START_MONTH} through {END_MONTH}")

    for file_path in files:
        monthly_df = pd.read_csv(file_path, low_memory=False)

        if "filled" in file_path.stem.lower():
            monthly_df = monthly_df.drop(
                columns=["latfilled", "lonfilled"],
                errors="ignore"
            )

        total_before_concat += len(monthly_df)
        frames.append(monthly_df)
        print(f"{file_path.name}: {len(monthly_df):,} rows")

    combined_df = pd.concat(frames, ignore_index=True)

    # Row-count confirmation before and after concatenation.
    print(f"Rows before concatenation: {total_before_concat:,}")
    print(f"Rows after concatenation:  {len(combined_df):,}")
    assert total_before_concat == len(combined_df)

    if "PropertyType" not in combined_df.columns:
        raise KeyError(f"'PropertyType' is missing from the {dataset_name} data.")

    rows_before_filter = len(combined_df)
    residential_df = combined_df.loc[
        combined_df["PropertyType"].eq("Residential")
    ].copy()

    # Row-count confirmation before and after the Residential filter.
    print(f"Rows before Residential filter: {rows_before_filter:,}")
    print(f"Rows after Residential filter:  {len(residential_df):,}")

    return residential_df


def main():
    sold_residential = combine_and_filter(SOLD_PREFIX, "sold")
    listings_residential = combine_and_filter(LISTING_PREFIX, "listings")

    sold_output = DATA_DIR / "combined_sold_residential.csv"
    listings_output = DATA_DIR / "combined_listings_residential.csv"

    sold_residential.to_csv(sold_output, index=False)
    listings_residential.to_csv(listings_output, index=False)

    print("\nOUTPUT FILES")
    print(sold_output)
    print(listings_output)


if __name__ == "__main__":
    main()
