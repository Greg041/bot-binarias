import pandas as pd
import numpy as np


def ADX(data, periodos):
    dataframe_tr = pd.DataFrame()
    dataframe_tr["H-L"] = abs(data["h"] - data["l"])
    dataframe_tr["H-CA"] = abs(data["h"] - data["c"].shift(1))
    dataframe_tr["L-CA"] = abs(data["l"] - data["c"].shift(1))
    dataframe_tr["TR"] = dataframe_tr.max(axis=1, skipna=False)
    data_adx = pd.DataFrame()
    data_adx['DMplus'] = np.where((data['h'] - data['h'].shift(1)) > (data['l'].shift(1) - data['l']),
                                  data['h'] - data['h'].shift(1), 0)
    data_adx['DMminus'] = np.where((data['l'].shift(1) - data['l']) > (data['h'] - data['h'].shift(1)),
                                   data['l'].shift(1) - data['l'], 0)
    TRn = []
    DMplusN = []
    DMminusN = []
    TR = dataframe_tr['TR'].tolist()
    DMplus = data_adx['DMplus'].tolist()
    DMminus = data_adx['DMminus'].tolist()
    for i in range(len(data_adx)):
        if i < periodos:
            TRn.append(np.NaN)
            DMplusN.append(np.NaN)
            DMminusN.append(np.NaN)
        elif i == periodos:
            TRn.append(dataframe_tr['TR'].rolling(periodos).sum().tolist()[periodos])
            DMplusN.append(data_adx['DMplus'].rolling(periodos).sum().tolist()[periodos])
            DMminusN.append(data_adx['DMminus'].rolling(periodos).sum().tolist()[periodos])
        elif i > periodos:
            TRn.append(TRn[i-1] - (TRn[i-1]/14) + TR[i])
            DMplusN.append(DMplusN[i-1] - (DMplusN[i-1]/14) + DMplus[i])
            DMminusN.append(DMminusN[i-1] - (DMminusN[i-1]/14) + DMminus[i])
    data_adx['TRn'] = np.array(TRn)
    data_adx['DMplusN'] = np.array(DMplusN)
    data_adx['DMminusN'] = np.array(DMminusN)
    data_adx['DIplusN'] = 100 * (data_adx['DMplusN'] / data_adx['TRn'])
    data_adx['DIminusN'] = 100 * (data_adx['DMminusN'] / data_adx['TRn'])
    data_adx['DIdiff'] = abs(data_adx['DIplusN'] - data_adx['DIminusN'])
    data_adx['DIsum'] = data_adx['DIplusN'] + data_adx['DIminusN']
    data_adx['DX'] = 100 * (data_adx['DIdiff'] / data_adx['DIsum'])
    ADX = []
    DX = data_adx['DX'].tolist()
    for j in range(len(data_adx)):
        if j < 2 * periodos - 1:
            ADX.append(np.NaN)
        elif j == 2 * periodos - 1:
            ADX.append(data_adx['DX'][j-periodos+1:j+1].mean())
        elif j > 2 * periodos - 1:
            ADX.append(((periodos - 1) * ADX[j - 1] + DX[j]) / periodos)
    adx = pd.DataFrame()
    adx["ADX"] = np.array(ADX)
    adx["DI-"] = data_adx["DIminusN"]
    adx["DI+"] = data_adx["DIplusN"]
    adx.dropna(inplace=True)
    return adx