import pandas as pd


def ichimoku(ohlc, tenkan_period=9, kijun_period=26, sspanB_period=52):
    ichimoku = pd.DataFrame()
    # tenkan-sen(conversion line) calculation
    tenkan_period_high = ohlc['h'].rolling(tenkan_period).max()
    tenkan_period_low = ohlc['l'].rolling(tenkan_period).min()
    ichimoku["tenkan-sen"] = (tenkan_period_high + tenkan_period_low) / 2
    # Kijun-sen(base line) calculation
    kijun_period_high = ohlc['h'].rolling(kijun_period).max()
    kijun_period_low = ohlc['l'].rolling(kijun_period).min()
    ichimoku["kijun-sen"] = (kijun_period_high + kijun_period_low) / 2
    # Senkou span A (Leading span A) calculation
    ichimoku["Senkou span A"] = ((ichimoku["tenkan-sen"] + ichimoku["kijun-sen"]) / 2).shift(26)
    # Senkou span B (Leading span B) calculation
    sspanB_period_high = ohlc['h'].rolling(sspanB_period).max()
    sspanB_period_low = ohlc['l'].rolling(sspanB_period).min()
    ichimoku["Senkou span B"] = ((sspanB_period_high + sspanB_period_low) / 2).shift(26)
    # Chikou span calculation
    ichimoku["Chikou"] = ohlc['c'].shift(-26)
    return ichimoku

