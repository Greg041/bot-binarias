import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import pandas as pd
import time
from multiprocessing import Process


class ExtraccionOanda(Process):
    def __init__(self, numero_de_velas, timeframe, par_de_divisas):
        super().__init__()
        self.starttime = time.time()
        self.numero_de_velas = numero_de_velas
        self.timeframe = timeframe
        self.par_de_divisas = par_de_divisas
        self.params = {"count": self.numero_de_velas, "granularity": self.timeframe}  # granularity can be in seconds S5 -
        # S30, minutes M1 - M30, hours H1 - H12, days D, weeks W or months M
        self.client = oandapyV20.API(access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                                     environment="practice")

    def run(self):
        starttime = time.time()
        contador_primera_vez = 0
        self.candles = instruments.InstrumentsCandles(instrument=self.par_de_divisas, params=self.params)
        temporalidad = (5 if (self.timeframe == "S5") else
                        30 if (self.timeframe == "S30") else
                        60 if (self.timeframe == "M1") else
                        300 if (self.timeframe == "M5") else
                        600 if (self.timeframe == "M10") else
                        900 if (self.timeframe == "M15") else
                        1800 if (self.timeframe == "M30") else
                        3600 if (self.timeframe == "H1") else
                        0)
        while True:
            try:
                starttime2 = time.time()
                self.client.request(self.candles)
                ohlc_dict = self.candles.response["candles"]
                ohlc = pd.DataFrame(ohlc_dict)
                ohlc_df = ohlc.mid.dropna().apply(pd.Series)
                ohlc_df["volume"] = ohlc["volume"]
                ohlc_df.index = ohlc["time"]
                ohlc_df = ohlc_df.apply(pd.to_numeric)
                pd.DataFrame.to_csv(ohlc_df, f"datos_{self.timeframe}.csv")
                if contador_primera_vez == 0:
                    time.sleep(temporalidad - ((time.time() - starttime) % temporalidad))
                    contador_primera_vez += 1
                else:
                    time.sleep(temporalidad - ((time.time() - starttime2) % temporalidad))
            except:
                print("hubo un error en extraccion oanda")
                starttime = time.time()
                self.params = {"count": self.numero_de_velas,
                               "granularity": self.timeframe}  # granularity can be in seconds S5 -
                # S30, minutes M1 - M30, hours H1 - H12, days D, weeks W or months M
                self.client = oandapyV20.API(
                    access_token="e51f5c80499fd16ae7e9ff6676b3c53f-3ac97247f6df3ad7b2b3731a4b1c2dc3",
                    environment="practice")
                self.candles = instruments.InstrumentsCandles(instrument=self.par_de_divisas, params=self.params)
                self.client.request(self.candles)
                ohlc_dict = self.candles.response["candles"]
                ohlc = pd.DataFrame(ohlc_dict)
                ohlc_df = ohlc.mid.dropna().apply(pd.Series)
                ohlc_df["volume"] = ohlc["volume"]
                ohlc_df.index = ohlc["time"]
                ohlc_df = ohlc_df.apply(pd.to_numeric)
                pd.DataFrame.to_csv(ohlc_df, f"datos_{self.timeframe}.csv")
                time.sleep(temporalidad - ((time.time() - starttime) % temporalidad))