from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd


class SalesDataError(ValueError):
    """Raised when the sales data is invalid or insufficient for comparison."""


@dataclass
class MetricSummary:
    yearly_totals: Dict[int, float]
    yoy_growth: Dict[int, Optional[float]]


@dataclass
class ProductSummary:
    product: str
    metrics: Dict[str, MetricSummary]


@dataclass
class ComparisonReport:
    products: Dict[str, ProductSummary]
    yearly_deltas: Dict[int, Dict[str, Dict[str, Optional[float]]]]
    period_start: pd.Timestamp
    period_end: pd.Timestamp
    monthly_breakdown: pd.DataFrame


class SalesComparisonAgent:
    """Agent responsible for comparing sales metrics across two CPG products."""

    REQUIRED_COLUMNS = {"date", "product", "units_sold", "revenue"}
    METRICS = ("units_sold", "revenue")

    def __init__(self, data_path: Path | str) -> None:
        self.data_path = Path(data_path)
        self._df = self._load()

    @property
    def data(self) -> pd.DataFrame:
        return self._df.copy()

    def available_products(self) -> List[str]:
        return sorted(self._df["product"].unique().tolist())

    def compare(self, product_a: str, product_b: str) -> ComparisonReport:
        self._validate_products([product_a, product_b])
        filtered = self._filter_products([product_a, product_b])
        last_two_years = self._restrict_last_two_years(filtered)

        if last_two_years["date"].dt.year.nunique() < 2:
            raise SalesDataError("At least two distinct years of data are required for comparison.")

        monthly = last_two_years.sort_values(["date", "product"]).set_index(["date", "product"])

        yearly_totals = (
            last_two_years.assign(year=last_two_years["date"].dt.year)
            .groupby(["product", "year"])[list(self.METRICS)]
            .sum()
        )

        products: Dict[str, ProductSummary] = {}
        for product in [product_a, product_b]:
            metrics: Dict[str, MetricSummary] = {}
            product_totals = yearly_totals.loc[product]
            for metric in self.METRICS:
                yearly_metric_totals = product_totals[metric].to_dict()
                yoy = self._compute_yoy_growth(yearly_metric_totals)
                metrics[metric] = MetricSummary(yearly_totals=yearly_metric_totals, yoy_growth=yoy)

            products[product] = ProductSummary(product=product, metrics=metrics)

        yearly_deltas = self._compute_yearly_deltas(yearly_totals, product_a, product_b)

        period_start = monthly.index.get_level_values("date").min()
        period_end = monthly.index.get_level_values("date").max()

        monthly_breakdown = (
            monthly.reset_index()[["date", "product", *self.METRICS]]
            .pivot(index="date", columns="product", values=self.METRICS)
            .sort_index()
        )
        monthly_breakdown.columns = [
            f"{metric}:{product}" for metric, product in monthly_breakdown.columns
        ]

        return ComparisonReport(
            products=products,
            yearly_deltas=yearly_deltas,
            period_start=period_start,
            period_end=period_end,
            monthly_breakdown=monthly_breakdown,
        )

    def format_report(self, report: ComparisonReport) -> str:
        lines: List[str] = []
        lines.append(
            f"Comparison window: {report.period_start:%Y-%m} to {report.period_end:%Y-%m}"
        )
        lines.append("")
        for product, summary in report.products.items():
            lines.append(product)
            for metric in self.METRICS:
                metric_summary = summary.metrics[metric]
                lines.append(f"  {metric.replace('_', ' ').title()} totals:")
                for year in sorted(metric_summary.yearly_totals):
                    total = metric_summary.yearly_totals[year]
                    yoy = metric_summary.yoy_growth.get(year)
                    yoy_text = "n/a" if yoy is None else f"{yoy:.1%}"
                    lines.append(f"    {year}: {total:,.0f} (YoY: {yoy_text})")
            lines.append("")

        lines.append("Year-over-year product deltas")
        for year in sorted(report.yearly_deltas):
            lines.append(f"  {year}")
            for metric in self.METRICS:
                delta = report.yearly_deltas[year][metric]
                absolute = delta["absolute"]
                percentage = delta["percentage"]
                percent_text = "n/a" if percentage is None else f"{percentage:.1%}"
                leader = delta["leader"]
                lines.append(
                    f"    {metric.replace('_', ' ').title()}: "
                    f"{absolute:,.0f} difference ({percent_text}), leader: {leader}"
                )
        return "\n".join(lines)

    def report_to_dict(self, report: ComparisonReport) -> Dict[str, Any]:
        return {
            "period": {
                "start": report.period_start.strftime("%Y-%m-%d"),
                "end": report.period_end.strftime("%Y-%m-%d"),
            },
            "products": {
                name: {
                    metric: {
                        "yearly_totals": summary.metrics[metric].yearly_totals,
                        "yoy_growth": summary.metrics[metric].yoy_growth,
                    }
                    for metric in self.METRICS
                }
                for name, summary in report.products.items()
            },
            "yearly_deltas": report.yearly_deltas,
            "monthly_breakdown": report.monthly_breakdown.reset_index().to_dict(
                orient="records"
            ),
        }

    def plot_monthly_metric(
        self,
        report: ComparisonReport,
        metric: str,
        output_path: Path | str,
    ) -> Path:
        if metric not in self.METRICS:
            raise ValueError(f"Unsupported metric '{metric}'. Choose from {self.METRICS}.")
        output_path = Path(output_path)
        monthly = report.monthly_breakdown.copy()

        try:
            import matplotlib.pyplot as plt
        except ImportError as exc:
            raise RuntimeError(
                "matplotlib is required for plotting. Install it or omit the plot option."
            ) from exc

        plt.figure(figsize=(10, 5))
        dates = monthly.index
        for product in report.products:
            column = f"{metric}:{product}"
            if column in monthly:
                plt.plot(dates, monthly[column], label=product)
        plt.title(f"Monthly {metric.replace('_', ' ').title()} Comparison")
        plt.xlabel("Date")
        plt.ylabel(metric.replace("_", " ").title())
        plt.legend()
        plt.tight_layout()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path)
        plt.close()
        return output_path

    def _load(self) -> pd.DataFrame:
        if not self.data_path.exists():
            raise FileNotFoundError(f"Sales data file not found: {self.data_path}")
        df = pd.read_csv(self.data_path)
        missing = self.REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise SalesDataError(f"Sales data missing required columns: {', '.join(sorted(missing))}")
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        if df["date"].isna().any():
            bad_rows = df[df["date"].isna()]
            raise SalesDataError(f"Invalid date values detected in rows: {bad_rows.index.tolist()}")
        df["product"] = df["product"].astype(str).str.strip()
        for metric in self.METRICS:
            df[metric] = pd.to_numeric(df[metric], errors="coerce")
            if df[metric].isna().any():
                raise SalesDataError(f"Invalid numeric values detected in metric column '{metric}'.")
        return df

    def _validate_products(self, products: List[str]) -> None:
        available = set(self.available_products())
        missing = [p for p in products if p not in available]
        if missing:
            raise SalesDataError(f"Products not found in data: {', '.join(missing)}")

    def _filter_products(self, products: List[str]) -> pd.DataFrame:
        return self._df[self._df["product"].isin(products)].copy()

    def _restrict_last_two_years(self, df: pd.DataFrame) -> pd.DataFrame:
        monthly_periods = df["date"].dt.to_period("M")
        last_period = monthly_periods.max()
        if pd.isna(last_period):
            raise SalesDataError("Unable to determine latest date in dataset.")
        periods = {last_period - i for i in range(24)}
        filtered = df[monthly_periods.isin(periods)].copy()
        if filtered.empty:
            raise SalesDataError("No data found for the last two years.")
        return filtered

    @staticmethod
    def _compute_yoy_growth(yearly_totals: Dict[int, float]) -> Dict[int, Optional[float]]:
        yoy: Dict[int, Optional[float]] = {}
        previous_value: Optional[float] = None
        for year in sorted(yearly_totals):
            current_value = yearly_totals[year]
            if previous_value is None or previous_value == 0:
                yoy[year] = None
            else:
                yoy[year] = (current_value - previous_value) / previous_value
            previous_value = current_value
        return yoy

    def _compute_yearly_deltas(
        self,
        yearly_totals: pd.DataFrame,
        product_a: str,
        product_b: str,
    ) -> Dict[int, Dict[str, Dict[str, Optional[float]]]]:
        deltas: Dict[int, Dict[str, Dict[str, Optional[float]]]] = {}
        years = sorted(yearly_totals.index.get_level_values("year").unique())
        for year in years:
            deltas[year] = {}
            for metric in self.METRICS:
                val_a = yearly_totals.loc[(product_a, year)][metric]
                val_b = yearly_totals.loc[(product_b, year)][metric]
                absolute = val_a - val_b
                percentage = None if val_b == 0 else absolute / val_b
                if val_a == val_b:
                    leader = \"tie\"
                else:
                    leader = product_a if val_a > val_b else product_b
                deltas[year][metric] = {
                    \"absolute\": float(absolute),
                    \"percentage\": None if percentage is None else float(percentage),
                    \"leader\": leader,
                }
        return deltas
