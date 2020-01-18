import pandas as pd


def MACD(DF, periodo_rapido=12, periodo_lento=26, periodo_señal=9):
    """function to calculate MACD
       typical values a = 12; b =26, c =9"""
    df = pd.DataFrame()
    df["MA_Fast"] = DF['c'].ewm(span=periodo_rapido, min_periods=periodo_rapido).mean()
    df["MA_Slow"] = DF['c'].ewm(span=periodo_lento, min_periods=periodo_lento).mean()
    df["MACD"] = df["MA_Fast"] - df["MA_Slow"]
    df["Signal"] = df["MACD"].ewm(span=periodo_señal, min_periods=periodo_señal).mean()
    df["historigrama"] = df["MACD"] - df["Signal"]
    df.dropna(inplace=True)
    return df


def detectar_div_macd(macd_df, ohlc, tipo_de_divergencia):
    if tipo_de_divergencia == "bajista":
        # Se realiza una inspección en retroceso para encontrar el último y el penúltimo pico en el macd y se
        # identifica el high en el precio en dichos picos
        pico_max2_macd = 0
        pico_max1_macd = 0
        valor_precio_max2 = 0
        valor_precio_max1 = 0
        for valor in range(1, 101):
            if pico_max2_macd == 0:
                if (macd_df["MACD"].iloc[-(valor + 1)] > 0) and \
                        (macd_df["MACD"].iloc[-valor] < macd_df["MACD"].iloc[-(valor + 1)] >
                         macd_df["MACD"].iloc[-(valor + 2)] >= macd_df["MACD"].iloc[-(valor + 3)] >=
                         macd_df["MACD"].iloc[-(valor + 4)]):
                    pico_max2_macd = macd_df["MACD"].iloc[-(valor + 1)]
                    valor_precio_max2 = ohlc['h'].iloc[-(valor + 1)]
            elif pico_max2_macd != 0 and pico_max1_macd == 0:
                if (macd_df["MACD"].iloc[-(valor + 1)] > 0) and \
                        (macd_df["MACD"].iloc[-(valor - 2)] <= macd_df["MACD"].iloc[-(valor - 1)] <=
                         macd_df["MACD"].iloc[-valor] < macd_df["MACD"].iloc[-(valor + 1)] >
                         macd_df["MACD"].iloc[-(valor + 2)] >= macd_df["MACD"].iloc[-(valor + 3)] >=
                         macd_df["MACD"].iloc[-(valor + 4)]):
                    pico_max1_macd = macd_df["MACD"].iloc[-(valor + 1)]
                    valor_precio_max1 = ohlc['h'].iloc[-(valor + 1)]
            else:
                break
        if (pico_max1_macd > pico_max2_macd and valor_precio_max1 < valor_precio_max2) and \
                (macd_df["Signal"].iloc[-2] <= macd_df["MACD"].iloc[-2] and
                 macd_df["Signal"].iloc[-1] > macd_df["MACD"].iloc[-1]):
            return True
        else:
            return False
    elif tipo_de_divergencia == "alcista":
        pico_min2_macd = 0
        pico_min1_macd = 0
        valor_precio_min2 = 0
        valor_precio_min1 = 0
        for valor in range(1, 101):
            if pico_min2_macd == 0:
                if (macd_df["MACD"].iloc[-(valor + 1)] < 0) and \
                        (macd_df["MACD"].iloc[-valor] > macd_df["MACD"].iloc[-(valor + 1)] <
                         macd_df["MACD"].iloc[-(valor + 2)] <= macd_df["MACD"].iloc[-(valor + 3)] <=
                         macd_df["MACD"].iloc[-(valor + 4)]):
                    pico_min2_macd = macd_df["MACD"].iloc[-(valor + 1)]
                    valor_precio_min2 = ohlc['l'].iloc[-(valor + 1)]
            elif pico_min2_macd != 0 and pico_min1_macd == 0:
                if (macd_df["MACD"].iloc[-(valor + 1)] < 0) and \
                        (macd_df["MACD"].iloc[-(valor - 2)] >= macd_df["MACD"].iloc[-(valor - 1)] >=
                         macd_df["MACD"].iloc[-valor] > macd_df["MACD"].iloc[-(valor + 1)] <
                         macd_df["MACD"].iloc[-(valor + 2)] <= macd_df["MACD"].iloc[-(valor + 3)] <=
                         macd_df["MACD"].iloc[-(valor + 4)]):
                    pico_min1_macd = macd_df["MACD"].iloc[-(valor + 1)]
                    valor_precio_min1 = ohlc['l'].iloc[-(valor + 1)]
            else:
                break
        if (pico_min1_macd < pico_min2_macd and valor_precio_min1 > valor_precio_min2) and \
                (macd_df["Signal"].iloc[-2] >= macd_df["MACD"].iloc[-2] and
                 macd_df["Signal"].iloc[-1] < macd_df["MACD"].iloc[-1]):
            return True
        else:
            return False


def detectar_div_historigrama(macd_df, ohlc, tipo_de_divergencia):
    if tipo_de_divergencia == "bajista":
        # Se realiza una inspección en retroceso para encontrar el último y el penúltimo pico en el macd y se
        # identifica el high en el precio en dichos picos
        pico_max2_macd = 0
        pico_max1_macd = 0
        valor_precio_max2 = 0
        valor_precio_max1 = 0
        for valor in range(1, 101):
            if pico_max2_macd == 0:
                if (macd_df["historigrama"].iloc[-(valor + 1)] > 0) and \
                        (macd_df["historigrama"].iloc[-valor] < macd_df["historigrama"].iloc[-(valor + 1)] >
                         macd_df["historigrama"].iloc[-(valor + 2)] >= macd_df["historigrama"].iloc[-(valor + 3)] >=
                         macd_df["historigrama"].iloc[-(valor + 4)]):
                    pico_max2_macd = macd_df["historigrama"].iloc[-(valor + 1)]
                    valor_precio_max2 = ohlc['h'].iloc[-(valor + 1)]
            elif pico_max2_macd != 0 and pico_max1_macd == 0:
                if (macd_df["historigrama"].iloc[-(valor + 1)] > 0) and \
                        (macd_df["historigrama"].iloc[-(valor - 2)] <= macd_df["historigrama"].iloc[-(valor - 1)] <=
                         macd_df["historigrama"].iloc[-valor] < macd_df["historigrama"].iloc[-(valor + 1)] >
                         macd_df["historigrama"].iloc[-(valor + 2)] >= macd_df["historigrama"].iloc[-(valor + 3)] >=
                         macd_df["historigrama"].iloc[-(valor + 4)]):
                    pico_max1_macd = macd_df["historigrama"].iloc[-(valor + 1)]
                    valor_precio_max1 = ohlc['h'].iloc[-(valor + 1)]
            else:
                break
        if pico_max1_macd > pico_max2_macd and valor_precio_max1 < valor_precio_max2:
            return True
        else:
            return False
    elif tipo_de_divergencia == "alcista":
        pico_min2_macd = 0
        pico_min1_macd = 0
        valor_precio_min2 = 0
        valor_precio_min1 = 0
        for valor in range(1, 101):
            if pico_min2_macd == 0:
                if (macd_df["historigrama"].iloc[-(valor + 1)] < 0) and \
                        (macd_df["historigrama"].iloc[-valor] > macd_df["historigrama"].iloc[-(valor + 1)] <
                         macd_df["historigrama"].iloc[-(valor + 2)] <= macd_df["historigrama"].iloc[-(valor + 3)] <=
                         macd_df["historigrama"].iloc[-(valor + 4)]):
                    pico_min2_macd = macd_df["historigrama"].iloc[-(valor + 1)]
                    valor_precio_min2 = ohlc['l'].iloc[-(valor + 1)]
            elif pico_min2_macd != 0 and pico_min1_macd == 0:
                if (macd_df["historigrama"].iloc[-(valor + 1)] < 0) and \
                        (macd_df["historigrama"].iloc[-(valor - 2)] >= macd_df["historigrama"].iloc[-(valor - 1)] >=
                         macd_df["historigrama"].iloc[-valor] > macd_df["historigrama"].iloc[-(valor + 1)] <
                         macd_df["historigrama"].iloc[-(valor + 2)] <= macd_df["historigrama"].iloc[-(valor + 3)] <=
                         macd_df["historigrama"].iloc[-(valor + 4)]):
                    pico_min1_macd = macd_df["historigrama"].iloc[-(valor + 1)]
                    valor_precio_min1 = ohlc['l'].iloc[-(valor + 1)]
            else:
                break
        if pico_min1_macd < pico_min2_macd and valor_precio_min1 > valor_precio_min2:
            return True
        else:
            return False