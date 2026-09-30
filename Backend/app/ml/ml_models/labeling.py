""" 
label1 computation for supervised learning targets.
Label = 1 if price rises by more than k * atr within the next N candles , else 0 .
pure function - no DB access , operates on alreadu aligned series .

New improvision : computes  forward return labels and invalidates  windows containing timestamp gaps .

"""


import numpy as np 
import pandas as pd


# improved
MAX_ALLOWED_GAP_MINUTES = 3.0 # buffer allowed for minor delayed ticks 

def compute_forward_return_label(
    df : pd.DataFrame ,
    n_candles_ahead : int = 15 ,
    atr_multiplier : float = 1.0 ,
) -> pd.Series:

    """
    for each row i , looking at close [i + 1 : i + 1 +  n_candles_ahead] and checks wheather price rose above threshold = (close + (atr * atr_multiplier)).values at any point in that window .

    returns 0/1 labels aligned to close's index . The last n_candles_ahead rows get NaN ( no full forward window exists yet) - drop these before training 

    New improvision : compute binary target labels while invalodating rows where time gaps exist  within the forward horizon window.
    """

    """
    if len(close) != len(atr):
        raise ValueError("close and atr must be the same length and aligned")

    threshold = (close + (atr * atr_multiplier)).values
    close_values = close.values 
    n = len(close)

    label = pd.Series(index = close.index , dtype = "float64")

    for i in range(n):
        window_end = i + 1 + n_candles_ahead
        if window_end > n :
            label.iloc[i] = np.nan
            continue
        future_window = close_values[i + 1 : window_end]
        label.iloc[i] = 1.0 if future_window.max() > threshold[i] else 0.0

    return label

    """

    if "close" not in df or "atr" not in df or "timestamp" not in df :
        raise ValueError("DataFrame must contain 'close' , 'atr' , and 'timestamp' columns.")

    close = df["close"].values 
    atr = df["atr"].values 
    timestamp = pd.to_datetime(df["timestamp"]).values 
    n = len(df)

    labels = np.full(n , np.nan)
    # expected duration or N candles + buffer 

    max_duration_ns = np.timedelta64(n_candles_ahead + int(MAX_ALLOWED_GAP_MINUTES) , 'm')

    for i in range(n):
        window_end = i + 1 + n_candles_ahead
        if window_end > n :
            break # end of series reached

        # gap check : difference between timestamp at window_end -  1 and current timestamp 
        elapsed_time = timestamp[window_end - 1] - timestamp[i]
        if elapsed_time > max_duration_ns :
            continue # leaves a NaN due to internet disconnect gap 

        threshold = close[i] + (atr[i] * atr_multiplier)
        future_max = close[i + 1 : window_end].max()
        labels[i] = 1.0 if future_max > threshold else 0.0

    return pd.Series(labels , index = df.index , dtype="float64")
