from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .sales_agent import SalesComparisonAgent, SalesDataError

app = typer.Typer(add_completion=False)


@app.command(help="Compare sales metrics for two CPG products over the most recent two years.")
def compare(
    product_a: str = typer.Argument(..., help="Name of the first product."),
    product_b: str = typer.Argument(..., help="Name of the second product."),
    data_path: Path = typer.Option(
        Path("data/cpg_sales_two_years.csv"),
        "--data",
        "-d",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the sales data CSV.",
    ),
    output_json: Optional[Path] = typer.Option(
        None,
        "--json",
        help="Optional path to save the comparison report as JSON.",
    ),
    chart_path: Optional[Path] = typer.Option(
        None,
        "--chart",
        help="Optional path to save a monthly revenue chart (PNG).",
    ),
    chart_metric: str = typer.Option(
        "revenue",
        "--chart-metric",
        help="Metric to plot when --chart is provided. Options: revenue, units_sold.",
    ),
) -> None:
    try:
        agent = SalesComparisonAgent(data_path)
        report = agent.compare(product_a, product_b)
    except (FileNotFoundError, SalesDataError) as exc:
        typer.secho(f"Error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    typer.secho(agent.format_report(report), fg=typer.colors.GREEN)

    if output_json:
        output_json.parent.mkdir(parents=True, exist_ok=True)
        with output_json.open("w", encoding="utf-8") as f:
            json.dump(agent.report_to_dict(report), f, indent=2)
        typer.secho(f"JSON report saved to {output_json}", fg=typer.colors.BLUE)

    if chart_path:
        if chart_metric not in SalesComparisonAgent.METRICS:
            valid_options = ", ".join(SalesComparisonAgent.METRICS)
            typer.secho(
                f"Invalid chart metric '{chart_metric}'. Choose from: {valid_options}",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(code=1)
        try:
            agent.plot_monthly_metric(report, chart_metric, chart_path)
        except Exception as exc:  # noqa: BLE001
            typer.secho(f"Chart generation failed: {exc}", fg=typer.colors.RED, err=True)
        else:
            typer.secho(f"Chart saved to {chart_path}", fg=typer.colors.BLUE)


def run() -> None:
    app()


if __name__ == "__main__":
    run()
