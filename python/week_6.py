#!/usr/bin/env python3
"""
Week 6: Feature Engineering and Segmented Market Summary

Creates the following engineered metrics for sold residential listings:
- PriceRatio = ClosePrice / ListPrice
- CloseToOriginalListRatio = ClosePrice / OriginalListPrice
- PPSF = ClosePrice / LivingArea
- DaysOnMarket (standardized as numeric)
- YrMo = year-month extracted from CloseDate
- ListingToContractDays = PurchaseContractDate - ListingContractDate
- ContractToCloseDays = CloseDate - PurchaseContractDate

Outputs:
- featured_sold.csv
- week_6_sample_output.csv
- week_6_segment_summary.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


DATE_COLUMNS = [
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate"
]

NUMERIC_COLUMNS = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "DaysOnMarket"
]

ENGINEERED_COLUMNS = [
    "PriceRatio",
    "CloseToOriginalListRatio",
    "PPSF",
    "DaysOnMarket",
    "YrMo",
    "ListingToContractDays",
    "ContractToCloseDays"
]


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Divide only when both values are present and the denominator is positive."""
    result = numerator.div(denominator)
    return result.where(numerator.notna() & denominator.gt(0)).replace([np.inf, -np.inf], np.nan)


def engineer_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Convert source columns and create all required Week 6 metrics."""
    data = df.copy()

    required_columns = [
        "ClosePrice",
        "ListPrice",
        "OriginalListPrice",
        "LivingArea",
        "DaysOnMarket",
        "CloseDate",
        "PurchaseContractDate",
        "ListingContractDate"
    ]

    missing_columns = [column for column in required_columns if column not in data.columns]
    if missing_columns:
        raise KeyError(f"Missing required columns: {missing_columns}")

    data[DATE_COLUMNS] = data[DATE_COLUMNS].apply(pd.to_datetime, errors="coerce")
    data[NUMERIC_COLUMNS] = data[NUMERIC_COLUMNS].apply(pd.to_numeric, errors="coerce")

    data["PriceRatio"] = safe_divide(data["ClosePrice"], data["ListPrice"])
    data["CloseToOriginalListRatio"] = safe_divide(data["ClosePrice"], data["OriginalListPrice"])
    data["PPSF"] = safe_divide(data["ClosePrice"], data["LivingArea"])
    data["YrMo"] = data["CloseDate"].dt.to_period("M").astype("string")
    data["ListingToContractDays"] = (data["PurchaseContractDate"] - data["ListingContractDate"]).dt.days
    data["ContractToCloseDays"] = (data["CloseDate"] - data["PurchaseContractDate"]).dt.days

    # Negative durations indicate inconsistent source dates, so they are not used as valid metrics.
    data["ListingToContractDays"] = data["ListingToContractDays"].where(data["ListingToContractDays"] >= 0)
    data["ContractToCloseDays"] = data["ContractToCloseDays"].where(data["ContractToCloseDays"] >= 0)

    return data


def create_sample_output(data: pd.DataFrame, sample_size: int = 10) -> pd.DataFrame:
    """Return rows that demonstrate the engineered columns with populated values."""
    identifier_columns = [
        column for column in [
            "ListingKey",
            "PropertyType",
            "CountyOrParish",
            "ClosePrice",
            "ListPrice",
            "OriginalListPrice",
            "LivingArea",
            "CloseDate",
            "ListingContractDate",
            "PurchaseContractDate"
        ]
        if column in data.columns
    ]

    complete_sample = data.dropna(subset=ENGINEERED_COLUMNS).head(sample_size)

    if len(complete_sample) < sample_size:
        ranked_index = data[ENGINEERED_COLUMNS].notna().sum(axis=1).sort_values(ascending=False).index
        complete_sample = data.loc[ranked_index].head(sample_size)

    sample = complete_sample[identifier_columns + ENGINEERED_COLUMNS].copy()

    round_columns = [
        "PriceRatio",
        "CloseToOriginalListRatio",
        "PPSF"
    ]
    sample[round_columns] = sample[round_columns].round(3)

    return sample


def create_segment_summary(data: pd.DataFrame, group_column: str) -> pd.DataFrame:
    """Create a market summary grouped by CountyOrParish or PropertyType."""
    if group_column not in data.columns:
        raise KeyError(f"Grouping column '{group_column}' is not present in the dataset.")

    if "ListingKey" in data.columns:
        grouped = data.groupby(group_column, dropna=False, observed=True)
        summary = grouped.agg(
            ListingCount=("ListingKey", "nunique"),
            AverageClosePrice=("ClosePrice", "mean"),
            AveragePriceRatio=("PriceRatio", "mean"),
            AverageCloseToOriginalListRatio=("CloseToOriginalListRatio", "mean"),
            AveragePPSF=("PPSF", "mean"),
            AverageDaysOnMarket=("DaysOnMarket", "mean"),
            AverageListingToContractDays=("ListingToContractDays", "mean"),
            AverageContractToCloseDays=("ContractToCloseDays", "mean")
        ).reset_index()
    else:
        grouped = data.groupby(group_column, dropna=False, observed=True)
        summary = grouped.agg(
            ListingCount=("ClosePrice", "size"),
            AverageClosePrice=("ClosePrice", "mean"),
            AveragePriceRatio=("PriceRatio", "mean"),
            AverageCloseToOriginalListRatio=("CloseToOriginalListRatio", "mean"),
            AveragePPSF=("PPSF", "mean"),
            AverageDaysOnMarket=("DaysOnMarket", "mean"),
            AverageListingToContractDays=("ListingToContractDays", "mean"),
            AverageContractToCloseDays=("ContractToCloseDays", "mean")
        ).reset_index()

    average_columns = [
        column for column in summary.select_dtypes(include="number").columns
        if column != "ListingCount"
    ]

    summary[average_columns] = summary[average_columns].round(2)
    return summary.sort_values("ListingCount", ascending=False).reset_index(drop=True)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Engineer Week 6 sold-listing metrics and summaries.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("/Users/kmaxx/Desktop/IDX-da/idx_data"),
        help="Directory containing the input CSV and receiving output CSV files."
    )
    parser.add_argument(
        "--input-file",
        default="cleaned_sold.csv",
        help="Name of the cleaned sold CSV inside --data-dir."
    )
    parser.add_argument(
        "--group-by",
        choices=[
            "CountyOrParish",
            "PropertyType"
        ],
        default="CountyOrParish",
        help="Column used for the segmented summary."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    input_path = args.data_dir / args.input_file

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    sold_df = pd.read_csv(input_path, low_memory=False)
    featured_sold = engineer_metrics(sold_df)
    sample_output = create_sample_output(featured_sold)
    segment_summary = create_segment_summary(featured_sold, args.group_by)

    featured_path = args.data_dir / "featured_sold.csv"
    sample_path = args.data_dir / "week_6_sample_output.csv"
    summary_path = args.data_dir / "week_6_segment_summary.csv"

    featured_sold.to_csv(featured_path, index=False)
    sample_output.to_csv(sample_path, index=False)
    segment_summary.to_csv(summary_path, index=False)

    print("\nSAMPLE OUTPUT — ENGINEERED METRICS")
    print(sample_output.to_string(index=False))

    print(f"\nSEGMENTED SUMMARY BY {args.group_by}")
    print(segment_summary.head(15).to_string(index=False))

    print("\nFiles saved:")
    print(featured_path)
    print(sample_path)
    print(summary_path)


if __name__ == "__main__":
    main()
