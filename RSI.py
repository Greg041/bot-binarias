import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def RSI(data, periodo):
    df = data.copy()
    df['delta'] = df['c'] - df['c'].shift(1)
    df['gain'] = np.where(df['delta'] >= 0, df['delta'], 0)
    df['loss'] = np.where(df['delta'] < 0, abs(df['delta']), 0)
    avg_gain = []
    avg_loss = []
    gain = df['gain'].tolist()
    loss = df['loss'].tolist()
    for i in range(len(df)):
        if i < periodo:
            avg_gain.append(np.NaN)
            avg_loss.append(np.NaN)
        elif i == periodo:
            avg_gain.append(df['gain'].rolling(periodo).mean().tolist()[periodo])
            avg_loss.append(df['loss'].rolling(periodo).mean().tolist()[periodo])
        elif i > periodo:
            avg_gain.append(((periodo - 1) * avg_gain[i - 1] + gain[i]) / periodo)
            avg_loss.append(((periodo - 1) * avg_loss[i - 1] + loss[i]) / periodo)
    df['avg_gain'] = np.array(avg_gain)
    df['avg_loss'] = np.array(avg_loss)
    df['RS'] = df['avg_gain'] / df['avg_loss']
    df['RSI'] = 100 - (100 / (1 + df['RS']))
    return df['RSI']

