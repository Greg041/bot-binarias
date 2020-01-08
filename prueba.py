import fxcmpy
import pandas as pd
import time


def run(timeframe, numero_de_velas):
    print("comienza")
    starttime = time.time()
    contador_primera_vez = 0
    conexion = fxcmpy.fxcmpy(access_token="d576f8ce26454088fc3ae6fa8c6600ac5d96e174", log_level='error',
                             server='demo')
    temporalidad = (60 if (timeframe == "m1") else
                    300 if (timeframe == "m5") else
                    600 if (timeframe == "m10") else
                    900 if (timeframe == "m15") else
                    1800 if (timeframe == "m30") else
                    3600 if (timeframe == "H1") else
                    0)
    while True:
        starttime2 = time.time()
        data = conexion.get_candles("EUR/USD", period=timeframe, number=numero_de_velas)
        data.apply(pd.to_numeric)
        ohlc_df = pd.DataFrame()
        ohlc_df["o"] = (data.loc[:, "bidopen"] + data.loc[:, "askhigh"]) / 2
        ohlc_df["h"] = (data.loc[:, "bidhigh"] + data.loc[:, "askhigh"]) / 2
        ohlc_df["l"] = (data.loc[:, "bidlow"] + data.loc[:, "asklow"]) / 2
        ohlc_df["c"] = (data.loc[:, "bidclose"] + data.loc[:, "askclose"]) / 2
        ohlc_df["resistencia"] = ohlc_df["h"].rolling(150).max()
        ohlc_df["soporte"] = ohlc_df["l"].rolling(150).min()
        print(ohlc_df)
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        if contador_primera_vez == 0:
            time.sleep(temporalidad - ((time.time() - starttime) % temporalidad) - 5)
            contador_primera_vez += 1
        else:
            time.sleep((temporalidad - ((time.time() - starttime2) % temporalidad)) - 5)


if __name__ == "__main__":
    while time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) != f'2020-01-08 21:30:00':
        pass
    run("m1", 500)
