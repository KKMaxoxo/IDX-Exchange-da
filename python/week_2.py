"""
Week 2 EDA

For the combined sold and listing datasets, this script:
1. Documents all unique PropertyType values.
2. Filters to PropertyType == "Residential".
3. Produces null-count and missing-percentage summaries.
4. Flags columns with more than 90% missing values.
5. Summarizes ClosePrice, LivingArea, and DaysOnMarket using
   min, max, mean, median, and selected percentiles.
6. Saves each filtered Residential dataset and its EDA reports as CSV files.
"""

from pathlib import Path
import pandas as pd


# Update this path if your files are stored somewhere else.
DATA_DIR = Path("/Users/kmaxx/Desktop/IDX-da/idx_data")

INPUT_FILES = {
    "sold": DATA_DIR / "combined_sold.csv",
    "listing": DATA_DIR / "combined_listing.csv",
}

NUMERIC_COLUMNS = [
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket",
]


def create_null_summary(df):
    """Return missing counts and percentages for every column."""
    summary = pd.DataFrame({
        "Column": df.columns,
        "NullCount": df.isna().sum().values,
        "NullPercentage": (df.isna().mean().values * 100).round(2),
    })

    return summary.sort_values(
        ["NullPercentage", "NullCount"],
        ascending=[False, False],
    ).reset_index(drop=True)


def create_numeric_summary(df):
    """Return min, max, mean, median, and percentiles for required variables."""
    available_columns = [
        column
        for column in NUMERIC_COLUMNS
        if column in df.columns
    ]

    numeric_data = df[available_columns].apply(
        pd.to_numeric,
        errors="coerce",
    )

    summary = numeric_data.agg([
        "count",
        "min",
        "max",
        "mean",
        "median",
    ]).T

    percentiles = numeric_data.quantile([
        0.25,
        0.50,
        0.75,
        0.90,
        0.95,
        0.99,
    ]).T

    percentiles.columns = [
        "25thPercentile",
        "50thPercentile",
        "75thPercentile",
        "90thPercentile",
        "95thPercentile",
        "99thPercentile",
    ]

    summary["MissingCount"] = numeric_data.isna().sum()
    summary = summary.join(percentiles)

    column_order = [
        "count",
        "MissingCount",
        "min",
        "25thPercentile",
        "50thPercentile",
        "median",
        "75thPercentile",
        "90thPercentile",
        "95thPercentile",
        "99thPercentile",
        "max",
        "mean",
    ]

    return summary[column_order].round(2).reset_index(names="Variable")


def process_dataset(dataset_name, input_path):
    """Load, document, filter, summarize, and save one dataset."""
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_csv(input_path, low_memory=False)

    if "PropertyType" not in df.columns:
        raise KeyError(
            f"'PropertyType' was not found in {input_path.name}."
        )

    print(f"\n{'=' * 70}")
    print(f"{dataset_name.upper()} DATASET")
    print(f"{'=' * 70}")
    print(f"Input file: {input_path}")
    print(f"Rows before filtering: {len(df):,}")

    # Document all unique property types before applying the filter.
    unique_property_types = (
        df["PropertyType"]
        .astype("string")
        .dropna()
        .sort_values()
        .unique()
    )

    print("\nUnique PropertyType values found:")
    for property_type in unique_property_types:
        print(f"- {property_type}")

    # Filtering logic: retain only rows whose PropertyType is exactly Residential.
    residential_df = df.loc[
        df["PropertyType"].eq("Residential")
    ].copy()

    print("\nFiltering logic applied:")
    print('df["PropertyType"] == "Residential"')
    print(f"Rows after filtering: {len(residential_df):,}")
    print(f"Rows removed: {len(df) - len(residential_df):,}")

    null_summary = create_null_summary(residential_df)
    over_90_null = null_summary.loc[
        null_summary["NullPercentage"] > 90
    ].copy()
    numeric_summary = create_numeric_summary(residential_df)

    print("\nNull-count summary:")
    print(null_summary.to_string(index=False))

    print("\nColumns above 90% null:")
    if over_90_null.empty:
        print("None")
    else:
        print(over_90_null.to_string(index=False))

    print("\nNumeric distribution summary:")
    print(numeric_summary.to_string(index=False))

    filtered_output = DATA_DIR / f"{dataset_name}_residential_filtered.csv"
    null_output = DATA_DIR / f"{dataset_name}_null_summary.csv"
    over_90_output = DATA_DIR / f"{dataset_name}_over_90_percent_null.csv"
    numeric_output = DATA_DIR / f"{dataset_name}_numeric_summary.csv"

    residential_df.to_csv(filtered_output, index=False)
    null_summary.to_csv(null_output, index=False)
    over_90_null.to_csv(over_90_output, index=False)
    numeric_summary.to_csv(numeric_output, index=False)

    print("\nSaved files:")
    print(filtered_output)
    print(null_output)
    print(over_90_output)
    print(numeric_output)


def main():
    for dataset_name, input_path in INPUT_FILES.items():
        process_dataset(dataset_name, input_path)


if __name__ == "__main__":
    main()
