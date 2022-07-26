import click
import investor8_sdk
from pandas import DataFrame
from rich.console import Console

from i8_terminal.commands.earnings import earnings
from i8_terminal.common.cli import pass_command
from i8_terminal.common.formatting import get_formatter
from i8_terminal.common.layout import df2Table, format_df
from i8_terminal.common.stock_info import validate_ticker
from i8_terminal.types.ticker_param_type import TickerParamType


def get_hist_earnings_df(ticker: str, size: int) -> DataFrame:
    historical_earnings = investor8_sdk.EarningsApi().get_historical_earnings(ticker, size=size)
    historical_earnings = [d.to_dict() for d in historical_earnings]
    df = DataFrame(historical_earnings)
    df["period"] = df.fyq.str[2:-2] + " " + df.fyq.str[-2:]
    return df


def format_hist_earnings_df(df: DataFrame, target: str) -> DataFrame:
    formatters = {
        "actual_report_time": get_formatter("date", target),
        "eps_actual": get_formatter("number", target),
        "eps_ws": get_formatter("number", target),
        "eps_surprise": get_formatter("colorize_number", target),
        "revenue_actual": get_formatter("financial", target),
        "revenue_ws": get_formatter("financial", target),
        "revenue_surprise": get_formatter("colorize_financial", target),
    }
    col_names = {
        "actual_report_time": "Date",
        "period": "Period",
        "call_time": "Call Time",
        "eps_ws": "EPS Estimate",
        "eps_actual": "EPS Actual",
        "eps_surprise": "EPS Surprise",
        "revenue_ws": "Revenue Estimate",
        "revenue_actual": "Revenue Actual",
        "revenue_surprise": "Revenue Surprise",
    }
    return format_df(df, col_names, formatters)


@earnings.command()
@click.option("--ticker", "-k", type=TickerParamType(), required=True, callback=validate_ticker, help="Company ticker.")
@pass_command
def list(ticker: str) -> None:
    """
    Lists upcoming company earnings.

    Examples:

    `i8 earnings list --ticker AAPL`

    """
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        df = get_hist_earnings_df(ticker, size=10)
    df_formatted = format_hist_earnings_df(df, "console")
    table = df2Table(df_formatted)
    console.print(table)
