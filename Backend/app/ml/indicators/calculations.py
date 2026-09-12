"""
 vector calculations for techincal indicators.

 all function expect pandas objects and return pure pandas series/dataframes no database or state interactions allowed .

"""

import numpy as np 
import pandas as pd 
from app.ml.indicators.constants import(
    DEFAULT_MACD_FAST,
    DEFAULT_MACD_SIGNAL,
    DEFAULT_MACD_SLOW,
    DEFAULT_RSI_PERIOD,
    DEFAULT_SMA_PERIOD,
    DEFAULT_ADX_PERIOD,
    DEFAULT_ATR_PERIOD,
    DEFAULT_BB_PERIOD,
    DEFAULT_BB_STD_DEV,
    DEFAULT_STOCH_D_PERIOD,
    DEFAULT_STOCH_K_PERIOD,
    DEFAULT_EMA_PERIOD ,
    PPO_FAST_PERIOD,
    PPO_SLOW_PERIOD
)

def calculate_sma(
    series : pd.Series , period : int = DEFAULT_SMA_PERIOD
) -> pd.Series :

    """calculates simple moving average (SMA)"""

    if len(series) < period :
        return pd.Series(index = series.index , dtype="float64")
    return series.rolling(window=period).mean()

def calculate_ema(series: pd.Series, period: int = DEFAULT_EMA_PERIOD) -> pd.Series:
    """calculates exponential moving average (EMA)"""
    if len(series) < period:
        return pd.Series(index=series.index, dtype="float64")
    return series.ewm(span=period, adjust=False).mean()


def calculate_rsi(
        series : pd.Series , period : int = DEFAULT_RSI_PERIOD
) -> pd.Series :

    """calculate relative strength index (RSI) , using Wilder's smoothing method ."""
    if len(series) < period + 1 :
        return pd.Series(index = series.index , dtype="float64")

    delta = series.diff()  # .diff() returns the difference between each row and previous row , this gives price change per period 

    gain = delta.clip(lower = 0) # anything below 0 gets pushed up to 0 
    loss = -delta.clip(upper = 0)

    # wilder's expontential moving average
    avg_gain = gain.ewm(alpha = 1 / period , min_periods = period , adjust = False).mean()
    avg_loss = loss.ewm(alpha = 1 / period , min_periods = period , adjust = False).mean()

    # prevent divison by zero
    rs = avg_gain / avg_loss.replace(0 , np.nan)
    rsi = 100 - (100 / (1 + rs) )

    # handle edge cases : when loss is zero , RSI is 100 
    rsi = rsi.fillna(100.0)

    # if both gain and loss are 0 (flat price) , RSI is 50
    flat_mask = (avg_gain == 0 ) & (avg_loss == 0)
    rsi[flat_mask] = 50.0

    return rsi


def calculate_macd (
        series : pd.Series ,
        fast_period : int = DEFAULT_MACD_FAST ,
        slow_period : int = DEFAULT_MACD_SLOW ,
        signal_period : int = DEFAULT_MACD_SIGNAL ,
) -> pd.DataFrame :

    """ calculate macd line , signal line  and histogram

    returns dataframe with columns : [ 'macd' , 'macd_signal' , 'macd_hist']    
    """
    result = pd.DataFrame(
        index = series.index , columns = ["macd" , "macd_signal" , "macd_hist"] , dtype="float64"
    )

    if len(series) < slow_period :
        return result

    fast_ema = series.ewm(span=fast_period , adjust= False).mean()
    slow_ema = series.ewm(span=slow_period , adjust=False).mean()

    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal_period , adjust = False).mean()
    histogram = macd_line - signal_line

    result["macd"] = macd_line
    result["macd_signal"] = signal_line
    result["macd_hist"] = histogram

    return result


def calculate_bollinger_bands(
        series : pd.Series ,
        period : int = DEFAULT_BB_PERIOD ,
        std_dev : float = DEFAULT_BB_STD_DEV ,
) -> pd.DataFrame :

    """calculate bollinger bands (middle , upper , lower , bandwidth)
    
    return dataframe with columns : ['bb_middle" , "bb_upper" , "bb_lower" , 'bb_bandwidth']
    """

    result = pd.DataFrame(
        index = series.index ,
        columns = ["bb_middle" , "bb_upper" , "bb_lower" ,"bb_percent_b" ,"bb_bandwidth"],
        dtype="float64",
    )

    if len(series) < period :
        return result

    middle_band = series.rolling(window=period).mean()
    rolling_std = series.rolling(window=period).std(ddof=0)

    upper_band = middle_band + (rolling_std * std_dev)
    lower_band = middle_band - (rolling_std * std_dev)

    bandwidth = (upper_band - lower_band) / middle_band.replace(0, np.nan)
    percent_b = (series - lower_band) / (upper_band - lower_band).replace(0, np.nan)

    result["bb_middle"] = middle_band
    result["bb_upper"] = upper_band
    result["bb_lower"] = lower_band
    result["bb_percent_b"] = percent_b
    result["bb_bandwidth"] = bandwidth

    return result



def calculate_atr(
        df : pd.DataFrame , period : int = DEFAULT_ATR_PERIOD
) -> pd.Series :

    """calculate average true range (ATR) using wilder's smoothing method
    excepts dataframe with columns : ['high' , 'low' , 'close']
    """

    if len(df) < period + 1:
        return pd.Series(index = df.index , dtype = "float64")

    high = df["high"]
    low = df["low"]
    prev_close = df["close"].shift(1)

    tr1 =  high - low 
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    # true range is the maximum of the three components 

    tr = pd.concat([tr1 , tr2 , tr3] , axis=1).max(axis = 1)

    # wilder's exponential smoothing

    atr = tr.ewm(alpha = 1 / period , min_periods = period , adjust = False).mean()

    return atr


def calculate_adx(
        df: pd.DataFrame , period : int = DEFAULT_ADX_PERIOD
) -> pd.DataFrame :

    """calculate average directional index (ADX) , +DI , and -DI  using wilder's 
    smoothing 
    
    expects dataframe with columns : ['high' , 'low' , 'close']
    return dataframe with columns : ['plus_di' ,'minus_di' , 'adx']
    """
    result = pd.DataFrame(
        index = df.index , columns= ["plus_di" , "minus_di" , "adx"] , dtype="float64"
    )

    if len(df) < (period * 2):
        return result 

    high = df["high"]
    low = df["low"]

    up_move = high.diff()
    down_move = -low.diff()

    # Calculate Directional Movement (+DM, -DM)
    plus_dm = pd.Series(
        np.where((up_move > down_move) & (up_move > 0), up_move, 0.0), index=df.index
    )
    minus_dm = pd.Series(
        np.where((down_move > up_move) & (down_move > 0), down_move, 0.0), index=df.index
    )

    # True Range calculation
    atr = calculate_atr(df, period=period)

    # Smoother +DM and -DM using Wilder's formula
    smooth_plus_dm = plus_dm.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    smooth_minus_dm = minus_dm.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    # Directional Indicators (+DI, -DI)
    plus_di = 100 * (smooth_plus_dm / atr.replace(0, np.nan))
    minus_di = 100 * (smooth_minus_dm / atr.replace(0, np.nan))

    # Directional Index (DX)
    di_diff = (plus_di - minus_di).abs()
    di_sum = plus_di + minus_di
    dx = 100 * (di_diff / di_sum.replace(0, np.nan))

    # ADX is Wilder's smoothed average of DX
    adx = dx.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    result["plus_di"] = plus_di
    result["minus_di"] = minus_di
    result["adx"] = adx

    return result


def calculate_stochastic(
    df: pd.DataFrame,
    k_period: int = DEFAULT_STOCH_K_PERIOD,
    d_period: int = DEFAULT_STOCH_D_PERIOD,
) -> pd.DataFrame:
    """Calculate Stochastic Oscillator (%K and %D).

    Expects DataFrame with columns: ['high', 'low', 'close']
    Returns DataFrame with columns: ['stoch_k', 'stoch_d']
    """
    result = pd.DataFrame(
        index=df.index, columns=["stoch_k", "stoch_d"], dtype="float64"
    )

    if len(df) < k_period:
        return result

    low_min = df["low"].rolling(window=k_period).min()
    high_max = df["high"].rolling(window=k_period).max()

    # %K calculation with zero division protection
    denom = (high_max - low_min).replace(0, np.nan)
    stoch_k = 100 * ((df["close"] - low_min) / denom)
    stoch_k = stoch_k.fillna(50.0)  # Handle flat period edge-cases

    # %D calculation (SMA of %K)
    stoch_d = stoch_k.rolling(window=d_period).mean()

    result["stoch_k"] = stoch_k
    result["stoch_d"] = stoch_d

    return result

def calculate_obv(df: pd.DataFrame) -> pd.Series:
    """calculates on-balance volume (OBV)"""
    direction = np.sign(df["close"].diff()).fillna(0)
    return (direction * df["volume"]).cumsum()


def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    """calculates cumulative volume-weighted average price (VWAP)"""
    cum_vol = df["volume"].cumsum()
    cum_vol_price = (df["close"] * df["volume"]).cumsum()
    return cum_vol_price / cum_vol.replace(0, np.nan)

def calculate_ppo(
        series : pd.Series,
        fast_period : int = PPO_FAST_PERIOD ,
        slow_period : int = PPO_SLOW_PERIOD ,
)-> pd.Series :

    """percentage price oscillator - macd normalized as % of price ,so it's comparable acorss at any price scale."""

    if len(series) < slow_period :
        return pd.Series(index = series.index , dtype = "flaot64")

    fast_ema = series.ewm(span=fast_period , adjust=False).mean()
    slow_ema = series.ewm(span=slow_period , adjust=False).mean()

    return ((fast_ema - slow_ema)/ slow_ema.replace(0 , np.nan)) * 100.0