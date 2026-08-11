# California Real Estate Market Analytics

A data analytics project focused on cleaning, validating, analyzing, and visualizing California residential real estate data.

The project combines MLS listing and sold-property records to study market activity, pricing, sales performance, geographic patterns, property characteristics, and agent/office performance. The cleaned datasets are used to build an interactive Tableau dashboard with geographic and market-level filters.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Project Objectives](#project-objectives)
3. [Data](#data)
4. [Repository Structure](#repository-structure)
5. [Data Pipeline](#data-pipeline)
6. [Data Cleaning](#data-cleaning)
7. [Feature Engineering](#feature-engineering)
8. [Data Validation](#data-validation)
9. [Exploratory Data Analysis](#exploratory-data-analysis)
10. [Tableau Dashboard](#tableau-dashboard)
11. [Key Metrics](#key-metrics)
12. [Geographic Analysis](#geographic-analysis)
13. [Agent and Office Analysis](#agent-and-office-analysis)
14. [Filters and Interactivity](#filters-and-interactivity)
15. [Technologies](#technologies)
16. [How to Run the Project](#how-to-run-the-project)
17. [Known Limitations](#known-limitations)
18. [Future Improvements](#future-improvements)

---

# Project Overview

This project analyzes California residential real estate activity using MLS listing and closed-sale records.

The workflow consists of:

1. Importing raw MLS data
2. Standardizing data types and field formats
3. Identifying invalid or inconsistent records
4. Removing invalid geographic and date observations
5. Detecting and removing extreme numeric outliers
6. Creating analytical variables
7. Producing final cleaned listing and sold datasets
8. Performing exploratory analysis
9. Building an interactive Tableau dashboard

The final dashboard is designed to allow users to explore California housing market conditions across:

- Year
- Month
- County
- City
- ZIP code
- Property subtype

---

# Project Objectives

The project aims to answer questions such as:

### Market Activity

- How many new listings enter the market each month?
- How many properties close each month?
- How does market activity vary by year?
- How seasonal is the California housing market?

### Pricing

- How does median close price change over time?
- Which ZIP codes have the highest median close prices?
- How does pricing differ by property subtype?
- How closely do properties sell relative to their asking prices?

### Market Speed

- How many days does a property typically remain on the market?
- How does Days on Market vary by season?
- Which locations experience faster or slower transactions?

### Geographic Patterns

- Where are transactions concentrated?
- Which counties and ZIP codes have the highest sales activity?
- Which geographic areas have the highest median prices?

### Agent and Brokerage Performance

- Which listing agents generate the highest sales volume?
- Which agents close the largest number of units?
- Which listing offices generate the highest sales volume?
- How do agent rankings change when filtering by county, city, ZIP code, or property type?

---

# Data

The project uses two primary datasets.

## Sold Properties

Contains completed residential real estate transactions.

Important fields include:

### Pricing

- `ClosePrice`
- `ListPrice`
- `OriginalListPrice`

### Property Characteristics

- `LivingArea`
- `BedroomsTotal`
- `BathroomsTotalInteger`
- `PropertySubType`
- `YearBuilt`
- `LotSizeSquareFeet`
- `GarageSpaces`
- `ParkingTotal`

### Dates

- `CloseDate`
- `ListingContractDate`
- `PurchaseContractDate`

### Geography

- `City`
- `CountyOrParish`
- `PostalCode`
- `Latitude`
- `Longitude`

### Agent / Brokerage

- `ListAgentFullName`
- `ListOfficeName`
- `BuyerOfficeName`

---

## Active / Listing Properties

Contains properties listed on the market.

Important fields include:

- `ListPrice`
- `OriginalListPrice`
- `ListingContractDate`
- `PropertySubType`
- `City`
- `CountyOrParish`
- `PostalCode`
- `Latitude`
- `Longitude`
- `LivingArea`
- `BedroomsTotal`
- `BathroomsTotalInteger`
- `YearBuilt`

The listing dataset is primarily used to measure **new listing activity**, while the sold dataset is used to measure **closed transaction activity and realized prices**.

---

# Repository Structure

A recommended repository structure is:

```text
california-real-estate-analytics/
│
├── README.md
│
├── requirements.txt
│
├── .gitignore
│
├── LICENSE
│
├── data/
│   │
│   ├── raw/
│   │   ├── sold/
│   │   └── listings/
│   │
│   ├── interim/
│   │   ├── combined_sold.csv
│   │   └── combined_listing.csv
│   │
│   └── processed/
│       ├── sold_cleaned.csv
│       ├── listing_cleaned.csv
│       ├── sold_final_outliers_removed.csv
│       └── listing_final_outliers_removed.csv
│
├── notebooks/
│   │
│   ├── 01_data_import.ipynb
│   ├── 02_data_validation.ipynb
│   ├── 03_data_validation_EDA.ipynb
│   ├── 04_data_cleaning.ipynb
│   ├── 05_feature_engineering.ipynb
│   ├── 06_outlier_detection_removal.ipynb
│
├── src/
│   │
│   ├── __init__.py
│   ├── data_cleaning.py
│   ├── validation.py
│   ├── feature_engineering.py
│   ├── outliers.py
│   └── utils.py
│
├── tableau/
│   ├── california_real_estate_dashboard.twbx
│   └── screenshots/
│
├── reports/
│   ├── figures/
│   └── findings/
│
└── docs/
    ├── data_dictionary.md
    └── methodology.md