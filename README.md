## Sales Comparison Agent

Python agent that compares sales performance for two Consumer Packaged Goods (CPG) products—illustrated with Snickers Bar and Hershey's Bar—across the most recent two years contained in a structured dataset.

### Features
- Loads CSV-formatted monthly sales data.
- Summarizes yearly totals and year-over-year growth for `units_sold` and `revenue`.
- Highlights product deltas per year, including percentage differences and the leading product.
- CLI for quick comparisons, JSON export, and optional chart generation.
- Includes synthetic two-year dataset and automated tests.

### Getting Started
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the CLI**
   ```bash
   python -m src.cli compare "Snickers Bar" "Hersheys Bar" \
     --data data/cpg_sales_two_years.csv \
     --json artifacts/report.json \
     --chart artifacts/revenue.png
   ```
   Omit `--json` or `--chart` if you only need the console summary.

### Project Structure
- `data/cpg_sales_two_years.csv` – synthetic monthly sales data (24 months).
- `src/sales_agent.py` – comparison logic, reporting utilities, plotting helper.
- `src/cli.py` – Typer-based CLI entry point.
- `tests/test_sales_agent.py` – unit tests covering core behaviours.
- `docs/DESIGN.md` – design overview.

### Testing
```bash
pytest
```

### Extending
- Replace the data CSV with your own dataset, preserving required columns: `date`, `product`, `units_sold`, `revenue`.
- Add new metrics by updating `SalesComparisonAgent.METRICS` and adjusting summaries.
- Integrate other data sources by subclassing or adding loader utilities.
