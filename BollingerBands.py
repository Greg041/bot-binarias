import pandas as pd


def boll_bnd(ohlc, periodos=20):
    "function to calculate Bollinger Band"
    df = pd.DataFrame()
    df["MA"] = ohlc['c'].rolling(periodos).mean()
    df["BB_up"] = ohlc["MA"] + 2 * ohlc['c'].rolling(periodos).std(ddof=0)  # ddof=0 is required since we want to take the standard deviation of the population and not sample
    df["BB_dn"] = ohlc["MA"] - 2 * ohlc['c'].rolling(periodos).std(ddof=0)  # ddof=0 is required since we want to take the standard deviation of the population and not sample
    df["BB_width"] = ohlc["BB_up"] - ohlc["BB_dn"]
    df.dropna(inplace=True)
    return df
