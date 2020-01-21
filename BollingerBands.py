import pandas as pd


def boll_bnd(ohlc, periodos=20):
    "function to calculate Bollinger Band"
    df = pd.DataFrame()
    df["MA"] = ohlc['c'].rolling(periodos).mean()
    df["BB_up"] = df["MA"] + 2 * ohlc['c'].rolling(periodos).std(ddof=0)  # ddof=0 is required since we want to take the standard deviation of the population and not sample
    df["BB_dn"] = df["MA"] - 2 * ohlc['c'].rolling(periodos).std(ddof=0)  # ddof=0 is required since we want to take the standard deviation of the population and not sample
    df["BB_width"] = df["BB_up"] - df["BB_dn"]
    df.dropna(inplace=True)
    return df
