"""
Macro-economic reference data for the Nifty 50 analysis period.
Values reflect publicly reported RBI, MOSPI, and US Fed releases (Oct 2023 – Nov 2024).
Used to contextualize index performance for institutional investors.
"""

from typing import List, Dict, Any

ANALYSIS_PERIOD = "Oct 2023 – Nov 2024"


def get_india_macro_indicators() -> List[Dict[str, Any]]:
    """Key domestic indicators tracked by Indian banks and asset managers."""
    return [
        {
            "indicator": "RBI Repo Rate",
            "value": "6.50%",
            "as_of": "Held since Feb 2023",
            "trend": "Pause / Hawkish hold",
            "impact": "Higher rates raise borrowing costs for NBFCs and capex-heavy firms; supports bank NIMs but pressures valuations.",
        },
        {
            "indicator": "CPI Inflation (YoY)",
            "value": "4.87%",
            "as_of": "Oct 2024 (MOSPI)",
            "trend": "Cooling toward RBI 4% target",
            "impact": "Lower inflation improves odds of rate cuts — bullish for rate-sensitive sectors (Auto, Realty, Banks).",
        },
        {
            "indicator": "GDP Growth (Real)",
            "value": "~7.2%",
            "as_of": "FY 2023-24",
            "trend": "Strong vs global peers",
            "impact": "Robust domestic growth supports earnings for Consumer, IT services, and Industrials in the Nifty 50.",
        },
        {
            "indicator": "INR / USD",
            "value": "₹83.4 → ₹84.3",
            "as_of": "Period range",
            "trend": "Mild depreciation",
            "impact": "Weaker rupee helps IT exporters (TCS, INFY) but raises import costs for Oil & Gas and Aviation.",
        },
        {
            "indicator": "10Y G-Sec Yield",
            "value": "~6.85%",
            "as_of": "Nov 2024",
            "trend": "Elevated vs pre-COVID",
            "impact": "Higher bond yields compete with equities; institutions rotate between debt and large-cap index funds.",
        },
        {
            "indicator": "FII Net Flows",
            "value": "Volatile / net sell",
            "as_of": "CY 2023-24",
            "trend": "Outflows on global rate hikes",
            "impact": "FII selling pressure weighed on Nifty heavyweights; DII (mutual funds, LIC) provided offsetting support.",
        },
    ]


def get_us_macro_indicators() -> List[Dict[str, Any]]:
    """US indicators that drive global liquidity and institutional allocation to emerging markets."""
    return [
        {
            "indicator": "Fed Funds Rate",
            "value": "5.25% → 4.75%",
            "as_of": "Cuts began Sep 2024",
            "trend": "Peak then easing cycle",
            "impact": "High US rates pulled capital away from India; first cuts improved EM sentiment and Nifty flows.",
        },
        {
            "indicator": "US CPI (YoY)",
            "value": "3.2% → 2.6%",
            "as_of": "Oct 2023 → Oct 2024",
            "trend": "Disinflation",
            "impact": "Cooling US inflation enabled Fed pivot — reduces pressure on INR and supports risk assets globally.",
        },
        {
            "indicator": "US 10Y Treasury Yield",
            "value": "~4.3% → ~4.4%",
            "as_of": "Period average",
            "trend": "Sticky at multi-year highs",
            "impact": "Elevated US yields make dollar assets attractive; institutions hedge EM exposure when yields spike.",
        },
        {
            "indicator": "US Dollar Index (DXY)",
            "value": "~103 → ~107",
            "as_of": "Period range",
            "trend": "Strong dollar",
            "impact": "Strong dollar tightens global liquidity; EM equities including Nifty 50 often underperform in DXY rallies.",
        },
        {
            "indicator": "Brent Crude Oil",
            "value": "$84 → $73/bbl",
            "as_of": "Period range",
            "trend": "Declining",
            "impact": "Lower crude eases India's CAD and inflation — positive for OMCs (BPCL, ONGC) and macro stability.",
        },
        {
            "indicator": "US GDP Growth",
            "value": "~2.8%",
            "as_of": "2024 estimate",
            "trend": "Soft landing narrative",
            "impact": "Resilient US economy sustains IT export demand (Nifty IT basket) while delaying aggressive Fed cuts.",
        },
    ]


def get_macro_narrative() -> str:
    """Short institutional-style macro summary for the analysis window."""
    return (
        "During Oct 2023 – Nov 2024, Nifty 50 performance unfolded against a **tight global liquidity "
        "backdrop**: the US Fed held rates at 20-year highs before initiating cuts in late 2024, while RBI "
        "maintained a prolonged pause at 6.50%. Indian CPI cooled toward the 4% target, supporting the "
        "domestic growth story (~7% GDP). Institutions balanced **FII outflows** (driven by US yield "
        "advantage) with **DII buying**, while a strong dollar and elevated bond yields kept large banks "
        "and asset managers cautious on EM allocation. Rate-sensitive Nifty sectors (Banks, Auto, Realty) "
        "benefited from disinflation, while IT exporters gained from rupee weakness and resilient US demand."
    )
