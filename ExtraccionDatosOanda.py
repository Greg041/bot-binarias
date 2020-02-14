import oandapyV20.endpoints.instruments as instruments
import pandas as pd


def ExtraccionOanda(client, numero_de_velas, timeframe, par_de_divisas):
        numero_de_velas = numero_de_velas
        timeframe = timeframe
        par_de_divisas = par_de_divisas
        params = {"count": numero_de_velas, "granularity": timeframe}  # granularity can be in seconds S5 -
        # S30, minutes M1 - M30, hours H1 - H12, days D, weeks W or months M
        candles = instruments.InstrumentsCandles(instrument=par_de_divisas, params=params)
        client.request(candles)
        ohlc_dict = candles.response["candles"]
        ohlc = pd.DataFrame(ohlc_dict)
        ohlc_df = ohlc.mid.dropna().apply(pd.Series)
        ohlc_df["volume"] = ohlc["volume"]
        ohlc_df.index = ohlc["time"]
        ohlc_df = ohlc_df.apply(pd.to_numeric)
        pd.DataFrame.to_csv(ohlc_df, f"datos_{timeframe}.csv")
