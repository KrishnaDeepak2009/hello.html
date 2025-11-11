## Sales Comparison Agent Design

### Objective
Build a reusable Python-based agent that compares sales performance for two Consumer Packaged Goods (CPG) products—illustrated with Snickers Bar and Hershey's Bar—across the most recent two calendar years available in a structured dataset.

### Data Assumptions
- Input provided as a CSV file with at least: `date`, `product`, `units_sold`, `revenue`.
- `date` values represent the start of each monthly period.
- The file contains at least 24 consecutive months of data for both products.
- Additional products may be present; the agent filters to requested products.

### Core Components
- **`SalesComparisonAgent`**
  - Loads and validates data.
  - Filters the last two years relative to the latest `date` in the dataset.
  - Aggregates yearly totals for `units_sold` and `revenue`.
  - Calculates year-over-year growth and product deltas.
  - Generates a structured summary and optional chart/report artifacts.
- **CLI (`src/cli.py`)**
  - Accepts CSV path, product names, and output options.
  - Prints tabular summary and optionally saves JSON and chart outputs.
- **Visualization**
  - Optional Matplotlib line chart comparing monthly revenue trajectories.
- **Tests**
  - Validate aggregation logic and YOY calculations with fixture data.

### Output Metrics
- Yearly totals (`units_sold`, `revenue`) for each product.
- Year-over-year growth percentages for each metric.
- Absolute and percentage deltas between the two products per year.
- Identification of top performer per metric/year.

### Extensibility
- Support alternative time granularities with minor adjustments.
- Plug in external data sources by swapping the data loader.
- Export structured results (JSON, CSV) for downstream automation.
