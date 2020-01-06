import pandas as pd
import time
import fxcmpy
from multiprocessing import Process


class ExtraccionFxcmpy(Process):
    def __init__(self, numero_de_velas, timeframe, par_de_divisas):
        super().__init__()

        self.numero_de_velas = numero_de_velas
        self.timeframe = timeframe
        self.par_de_divisas = par_de_divisas

    def run(self):
        starttime = time.time()
        contador_primera_vez = 0
        conexion = fxcmpy.fxcmpy(access_token="d576f8ce26454088fc3ae6fa8c6600ac5d96e174", log_level='error',
                                      server='demo')
        temporalidad = (60 if (self.timeframe == "m1") else
                        300 if (self.timeframe == "m5") else
                        600 if (self.timeframe == "m10") else
                        900 if (self.timeframe == "m15") else
                        1800 if (self.timeframe == "m30") else
                        3600 if (self.timeframe == "H1") else
                        0)
        while True:
            starttime2 = time.time()
            data = conexion.get_candles(self.par_de_divisas, period=self.timeframe, number=self.numero_de_velas)
            data.apply(pd.to_numeric)
            ohlc_df = pd.DataFrame()
            ohlc_df["o"] = (data.loc[:, "bidopen"] + data.loc[:, "askhigh"]) / 2
            ohlc_df["h"] = (data.loc[:, "bidhigh"] + data.loc[:, "askhigh"]) / 2
            ohlc_df["l"] = (data.loc[:, "bidlow"] + data.loc[:, "asklow"]) / 2
            ohlc_df["c"] = (data.loc[:, "bidclose"] + data.loc[:, "askclose"]) / 2
            ohlc_df["resistencia"] = ohlc_df["h"].rolling(20).max()
            ohlc_df["soporte"] = ohlc_df["l"].rolling(20).min()
            pd.DataFrame.to_csv(ohlc_df, f"datos_{self.timeframe}.csv")
            if contador_primera_vez == 0:
                time.sleep(temporalidad - ((time.time() - starttime) % temporalidad) - 5)
                contador_primera_vez += 1
            else:
                time.sleep((temporalidad - ((time.time() - starttime2) % temporalidad)) - 5)
