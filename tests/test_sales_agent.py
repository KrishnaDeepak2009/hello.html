from pathlib import Path

import pytest

from src.sales_agent import ComparisonReport, SalesComparisonAgent, SalesDataError


DATA_PATH = Path(__file__).parents[1] / "data" / "cpg_sales_two_years.csv"


def _load_report() -> ComparisonReport:
    agent = SalesComparisonAgent(DATA_PATH)
    return agent.compare("Snickers Bar", "Hersheys Bar")


def test_compare_returns_two_years_of_data() -> None:
    report = _load_report()
    assert report.period_start.year < report.period_end.year
    for product_summary in report.products.values():
        for metric in SalesComparisonAgent.METRICS:
            yearly = product_summary.metrics[metric].yearly_totals
            assert len(yearly) == 2
            assert all(value > 0 for value in yearly.values())
            yoy_growth = product_summary.metrics[metric].yoy_growth
            assert yoy_growth[report.period_start.year] is None
            assert yoy_growth[report.period_end.year] is not None


def test_yearly_deltas_identify_leader_per_metric() -> None:
    report = _load_report()
    for year in report.yearly_deltas:
        for metric in SalesComparisonAgent.METRICS:
            leader = report.yearly_deltas[year][metric]["leader"]
            assert leader in {"Snickers Bar", "Hersheys Bar", "tie"}


def test_compare_with_unknown_product_raises() -> None:
    agent = SalesComparisonAgent(DATA_PATH)
    with pytest.raises(SalesDataError):
        agent.compare("Snickers Bar", "Nonexistent Bar")
