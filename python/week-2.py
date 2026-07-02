# =============================================================================
# 1. IMPORTS
# =============================================================================

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# =============================================================================
# 2. SETTINGS
# =============================================================================

# Change these paths to your combined raw CSV files.
# You can include only sold, only listing, or both.
INPUT_FILES = {
    "sold": "combined_output/CombinedSoldTransactions_Residential_202401_202605.csv",
    "listing": "combined_output/CombinedListingData_Residential_202401_202605.csv",
}

OUTPUT_DIR = Path("eda_output")
OUTPUT_DIR.mkdir(exist_ok=True)

CHARTS_DIR = OUTPUT_DIR / "charts"
CHARTS_DIR.mkdir(exist_ok=True)

OUTLIERS_DIR = OUTPUT_DIR / "outliers"
OUTLIERS_DIR.mkdir(exist_ok=True)

FILTER_PROPERTY_TYPE = "Residential"

KEY_NUMERIC_FIELDS = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt",
]

CORE_NUMERIC_SUMMARY_FIELDS = [
    "ClosePrice",
    "LivingArea",
    "DaysOnMarket",
]

CORE_FIELDS_TO_RETAIN = {
    "ListingKey",
    "ListingId",
    "PropertyType",
    "PropertySubType",
    "MlsStatus",
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt",
    "CloseDate",
    "ListingContractDate",
    "PurchaseContractDate",
    "City",
    "CountyOrParish",
    "StateOrProvince",
    "PostalCode",
    "Latitude",
    "Longitude",
}


# =============================================================================
# 3. HELPER FUNCTIONS
# =============================================================================

def clean_blank_values(df):
    """
    Replace blank strings and whitespace-only strings with missing values.
    """
    return df.replace(r"^\s*$", pd.NA, regex=True)


def document_unique_property_types(df, dataset_name):
    """
    Document unique PropertyType values found before filtering.
    """
    if "PropertyType" not in df.columns:
        raise ValueError(f"PropertyType column not found in {dataset_name}")

    property_type_summary = (
        df["PropertyType"]
        .fillna("Missing")
        .astype(str)
        .str.strip()
        .value_counts(dropna=False)
        .reset_index()
    )

    property_type_summary.columns = ["PropertyType", "RowCount"]
    property_type_summary["Dataset"] = dataset_name
    property_type_summary["Percent"] = (
        property_type_summary["RowCount"] / len(df) * 100
    ).round(2)

    property_type_summary = property_type_summary[
        ["Dataset", "PropertyType", "RowCount", "Percent"]
    ]

    output_path = OUTPUT_DIR / f"{dataset_name}_unique_property_types.csv"
    property_type_summary.to_csv(output_path, index=False)

    print("\nUnique property types found:")
    print(property_type_summary)

    return property_type_summary


def filter_to_residential(df, dataset_name):
    """
    Apply filtering logic:
        Keep only rows where PropertyType == 'Residential'
    """
    if "PropertyType" not in df.columns:
        raise ValueError(f"PropertyType column not found in {dataset_name}")

    rows_before_filter = len(df)

    print("\nFiltering logic applied:")
    print("Keep rows where PropertyType == 'Residential'")
    print(f"Rows before Residential filter: {rows_before_filter:,}")

    filtered_df = df[
        df["PropertyType"].astype(str).str.strip() == FILTER_PROPERTY_TYPE
    ].copy()

    rows_after_filter = len(filtered_df)

    print(f"Rows after Residential filter : {rows_after_filter:,}")
    print(f"Rows removed by filter        : {rows_before_filter - rows_after_filter:,}")

    return filtered_df


def create_missing_value_report(df, dataset_name):
    """
    Create a null-count summary table and flag columns above 90% null.
    """
    total_rows = len(df)

    records = []

    for col in df.columns:
        missing_count = df[col].isna().sum()
        missing_percent = (missing_count / total_rows * 100) if total_rows > 0 else 0

        high_missing = missing_percent > 90

        if col in CORE_FIELDS_TO_RETAIN:
            decision = "Retain core field"
        elif high_missing:
            decision = "Consider dropping; above 90% null"
        else:
            decision = "Retain or review"

        records.append({
            "Dataset": dataset_name,
            "Column": col,
            "MissingCount": missing_count,
            "MissingPercent": round(missing_percent, 2),
            "Above90PercentNull": high_missing,
            "DropOrRetainDecision": decision,
        })

    missing_report = pd.DataFrame(records)
    missing_report = missing_report.sort_values(
        by="MissingPercent",
        ascending=False
    )

    output_path = OUTPUT_DIR / f"{dataset_name}_missing_value_report.csv"
    missing_report.to_csv(output_path, index=False)

    print("\nMissing value report saved:")
    print(output_path)

    print("\nColumns above 90% null:")
    print(missing_report[missing_report["Above90PercentNull"] == True])

    return missing_report


def numeric_distribution_review(df, dataset_name):
    """
    For each key numeric field:
        - Convert to numeric
        - Produce histogram
        - Produce boxplot
        - Produce percentile summary
        - Identify extreme outliers using 3 * IQR rule
    """
    summary_records = []

    for field in KEY_NUMERIC_FIELDS:
        if field not in df.columns:
            summary_records.append({
                "Dataset": dataset_name,
                "Field": field,
                "Status": "Column not found",
            })
            continue

        values = pd.to_numeric(df[field], errors="coerce")
        non_missing_values = values.dropna()

        if non_missing_values.empty:
            summary_records.append({
                "Dataset": dataset_name,
                "Field": field,
                "Status": "No numeric values",
            })
            continue

        q1 = non_missing_values.quantile(0.25)
        q3 = non_missing_values.quantile(0.75)
        iqr = q3 - q1

        lower_outlier_bound = q1 - 3 * iqr
        upper_outlier_bound = q3 + 3 * iqr

        outlier_mask = (
            values < lower_outlier_bound
        ) | (
            values > upper_outlier_bound
        )

        outlier_rows = df.loc[outlier_mask].copy()
        outlier_output_path = OUTLIERS_DIR / f"{dataset_name}_{field}_extreme_outliers.csv"
        outlier_rows.to_csv(outlier_output_path, index=False)

        summary_records.append({
            "Dataset": dataset_name,
            "Field": field,
            "Status": "Analyzed",
            "Count": non_missing_values.count(),
            "MissingCount": values.isna().sum(),
            "Min": non_missing_values.min(),
            "Max": non_missing_values.max(),
            "Mean": non_missing_values.mean(),
            "Median": non_missing_values.median(),
            "P01": non_missing_values.quantile(0.01),
            "P05": non_missing_values.quantile(0.05),
            "P10": non_missing_values.quantile(0.10),
            "P25": non_missing_values.quantile(0.25),
            "P50": non_missing_values.quantile(0.50),
            "P75": non_missing_values.quantile(0.75),
            "P90": non_missing_values.quantile(0.90),
            "P95": non_missing_values.quantile(0.95),
            "P99": non_missing_values.quantile(0.99),
            "ExtremeOutlierLowerBound_3IQR": lower_outlier_bound,
            "ExtremeOutlierUpperBound_3IQR": upper_outlier_bound,
            "ExtremeOutlierCount": outlier_mask.sum(),
            "ExtremeOutlierFile": str(outlier_output_path),
        })

        # Histogram
        plt.figure()
        plt.hist(non_missing_values, bins=50)
        plt.title(f"{dataset_name}: {field} Histogram")
        plt.xlabel(field)
        plt.ylabel("Count")
        plt.tight_layout()
        histogram_path = CHARTS_DIR / f"{dataset_name}_{field}_histogram.png"
        plt.savefig(histogram_path)
        plt.close()

        # Boxplot
        plt.figure()
        plt.boxplot(non_missing_values)
        plt.title(f"{dataset_name}: {field} Boxplot")
        plt.ylabel(field)
        plt.tight_layout()
        boxplot_path = CHARTS_DIR / f"{dataset_name}_{field}_boxplot.png"
        plt.savefig(boxplot_path)
        plt.close()

    numeric_summary = pd.DataFrame(summary_records)

    output_path = OUTPUT_DIR / f"{dataset_name}_numeric_distribution_summary.csv"
    numeric_summary.to_csv(output_path, index=False)

    print("\nNumeric distribution summary saved:")
    print(output_path)

    return numeric_summary


def create_core_numeric_summary(numeric_summary, dataset_name):
    """
    Save a focused numeric summary for:
        ClosePrice, LivingArea, DaysOnMarket
    """
    core_summary = numeric_summary[
        numeric_summary["Field"].isin(CORE_NUMERIC_SUMMARY_FIELDS)
    ].copy()

    output_path = OUTPUT_DIR / f"{dataset_name}_core_numeric_summary.csv"
    core_summary.to_csv(output_path, index=False)

    print("\nCore numeric summary saved:")
    print(output_path)

    return core_summary


def process_dataset(dataset_name, input_path):
    """
    Full workflow for one dataset.
    """
    print("\n" + "=" * 90)
    print(f"PROCESSING DATASET: {dataset_name}")
    print("=" * 90)

    input_path = Path(input_path)

    if not input_path.exists():
        print(f"File not found, skipping: {input_path}")
        return

    # -------------------------------------------------------------------------
    # LOAD DATASET
    # -------------------------------------------------------------------------

    df = pd.read_csv(input_path, low_memory=False)
    df = clean_blank_values(df)

    print(f"Loaded file: {input_path}")
    print(f"Rows before filtering: {len(df):,}")
    print(f"Columns: {df.shape[1]:,}")

    # -------------------------------------------------------------------------
    # DOCUMENT UNIQUE PROPERTY TYPES
    # -------------------------------------------------------------------------

    document_unique_property_types(df, dataset_name)

    # -------------------------------------------------------------------------
    # FILTER TO RESIDENTIAL
    # -------------------------------------------------------------------------

    filtered_df = filter_to_residential(df, dataset_name)

    # -------------------------------------------------------------------------
    # NULL-COUNT SUMMARY AND MISSING VALUE REPORT
    # -------------------------------------------------------------------------

    create_missing_value_report(filtered_df, dataset_name)

    # -------------------------------------------------------------------------
    # NUMERIC DISTRIBUTION REVIEW
    # -------------------------------------------------------------------------

    numeric_summary = numeric_distribution_review(filtered_df, dataset_name)

    # -------------------------------------------------------------------------
    # CORE NUMERIC SUMMARY
    # -------------------------------------------------------------------------

    create_core_numeric_summary(numeric_summary, dataset_name)

    # -------------------------------------------------------------------------
    # SAVE FILTERED DATASET AS NEW CSV
    # -------------------------------------------------------------------------

    filtered_output_path = OUTPUT_DIR / f"{dataset_name}_Residential_Filtered.csv"
    filtered_df.to_csv(filtered_output_path, index=False)

    print("\nFiltered dataset saved:")
    print(filtered_output_path)


# =============================================================================
# 4. RUN SCRIPT
# =============================================================================

def main():
    for dataset_name, input_path in INPUT_FILES.items():
        process_dataset(dataset_name, input_path)

    print("\nDone.")


if __name__ == "__main__":
    main()