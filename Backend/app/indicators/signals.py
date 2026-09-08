
"""
functions for deriving categorical signals , statues , and metric deviations
consumes pandas series/dataframe produced by calculations.pyand return clean , vectorized pandas series representing operational states/enums .
"""

import numpy as np
import pandas as pd
from app.indicators.constants import (
    ADX_STRONG_THRESHOLD,
    ADX_WEAK_THRESHOLD,
    ATR_BASELINE_PERIOD,
    ATR_HIGH_MULTIPLIER,
    ATR_LOW_MULTIPLIER,
    BB_SQUEEZE_LOOKBACK,
    BB_SQUEEZE_PERCENTILE,
    FLAT_THRESHOLD_PCT,
    OBV_TREND_LOOKBACK,
    RSI_OVERBOUGHT_THRESHOLD,
    RSI_OVERSOLD_THRESHOLD,
    STOCH_OVERBOUGHT_THRESHOLD,
    STOCH_OVERSOLD_THRESHOLD,
)

# helper function to compute precentage slope safely

def calculate_pct_change( series : pd.Series , periods : int = 1 ) -> pd.Series:

    """calculates percentage change over N periods safely against zero division."""

    prev_series = series.shift(periods)
    denom = prev_series.abs().replace(0 , np.nan)
    return ((series - prev_series) / denom) * 100.0


# sma slop 
def derive_sma_slope(
        sma_series : pd.Series , flat_threshold_pct : float = FLAT_THRESHOLD_PCT
) -> pd.Series :

    """derive sma direction : 'rising' , 'falling' , or 'flat'."""

    pct_change = calculate_pct_change(sma_series , periods = 1)
    status = pd.Series("flat" , index= sma_series.index , dtype = "object")

    status[pct_change > flat_threshold_pct] = "rising"
    status[pct_change < -flat_threshold_pct] = "failling"
    status[sma_series.isna() | pct_change.isna()] = None 
    return status 

# ema_slope
def derive_ema_slope(
        ema_series : pd.Series , flat_threshold_pct : float = FLAT_THRESHOLD_PCT
) -> pd.Series :
    """derive ema direction : 'rising' , 'falling' , or 'flat'."""

    pct_change = calculate_pct_change(ema_series , periods = 1)
    status = pd.Series("flat" , index=ema_series.index , dtype ="object")

    status[pct_change > flat_threshold_pct] = "rising"
    status[pct_change < -flat_threshold_pct] = "falling"
    status[ema_series.isna() | pct_change.isna()] = None 

    return status 

# rsi status 
def derive_rsi_status(
        rsi_series : pd.Series,
        overbought : float = RSI_OVERBOUGHT_THRESHOLD ,
        oversold : float = RSI_OVERSOLD_THRESHOLD ,
) -> pd.Series :

    """Dervie RSI state : 'overbought' , 'oversold' , or 'neutral;' ."""
    status = pd.Series("neutral" , index = rsi_series.index , dtype = "object")

    status[rsi_series > overbought] = "overbought"
    status[rsi_series < oversold] = "oversold"
    status[rsi_series.isna()] = None 
    return status 

# macd crossover

def derive_macd_crossover( macd_df : pd.DataFrame) -> pd.Series :

    """derive macd crossover signal : 'bullish' , 'bearish' , or 'none'."""

    if "macd" not in macd_df or "macd_signal" not in macd_df :
        raise ValueError("Dataframe must contain 'macd' and 'macd_signal' columns.")

    macd = macd_df["macd"]
    signal = macd_df["macd_signal"]

    above = macd > signal 
    prev_above = above.shift(1)

    crossover = pd.Series("none" , index = macd_df.index , dtype ="object")

    crossover[(above == True) & (prev_above == False)] = "bullish"
    crossover[(above == False) & (prev_above == True)] = "bearish"
    crossover[macd.isna() | signal.isna() | prev_above.isna()] = None 

    return crossover

# macd hist direction

def derive_macd_hist_direction(
        macd_df : pd.DataFrame , flat_threshold_pct : float = FLAT_THRESHOLD_PCT
) -> pd.Series :
    """derive macd histogram direction : 'expanding' , 'contracting' , or 'flat'."""

    if "macd_hist" not in macd_df :
        raise ValueError("Dataframe must contain 'macd_hist' column.")

    hist = macd_df["macd_hist"]
    hist_mag = hist.abs()
    pct_change = calculate_pct_change(hist_mag , periods= 1)

    direction = pd.Series("flat" , index = macd_df.index , dtype = "object")

    direction[pct_change > flat_threshold_pct] = "expanding"
    direction[pct_change < -flat_threshold_pct] = "contracting"
    direction[hist.isna() | pct_change.isna()] = None 

    return direction


# bb_status 

def derive_bb_status(
        close_series : pd.Series,
        bb_df : pd.DataFrame ,
        squeeze_lookback : int = BB_SQUEEZE_LOOKBACK ,
        squeeze_percentile : int = BB_SQUEEZE_PERCENTILE ,
) -> pd.Series :

    """derive bollinger bands status : 'overbought' , 'oversold' ,'squeeze' , or 'normal'."""

    if "bb_upper" not in bb_df or "bb_lower" not in bb_df or "bb_bandwidth" not in bb_df :
        raise ValueError("DataFrame missing required Bollinger Band columns.")

    upper = bb_df["bb_upper"]
    lower = bb_df["bb_lower"]
    bandwidth = bb_df["bb_bandwidth"]

    # calculate precent %B (Close - lower) / (Upper -Lower)
    
    denom = (upper - lower).replace(0 , np.nan)
    percent_b = (close_series - lower) / denom

    # squeeze threshold dynamically set via rolling quantiles

    rolling_threshold = bandwidth.rolling(window = squeeze_lookback , min_periods = squeeze_lookback //  2).quantile(
        squeeze_percentile / 100.0
    )

    status = pd.Series( "normal" , index = close_series.index , dtype = "object")

    # order of evaluation : squeeze ta threshold bounds

    is_squeeze = bandwidth <= rolling_threshold
    status[is_squeeze] = "squeeze"
    status[percent_b > 1.0] = "overbought"
    status[percent_b < 0.0] = "oversold"

    status[close_series.isna() | upper.isna() | lower.isna() ] = None 

    return status 

# atr_vol_regime 

def derive_atr_vol_regime(
        atr_series : pd.Series ,
        baseline_period : int = ATR_BASELINE_PERIOD ,
        high_mult : float = ATR_HIGH_MULTIPLIER ,
        low_mult : float = ATR_LOW_MULTIPLIER ,
) -> pd.Series :

    """derive atr volatility regime : 'high' , 'low' , or 'normal'."""

    baseline = atr_series.rolling(window= baseline_period , min_periods = baseline_period).mean()

    regime = pd.Series("normal", index = atr_series.index , dtype = "object")

    regime[atr_series > (baseline * high_mult)] = "high"
    regime[atr_series < (baseline * low_mult)] = "low"
    regime[atr_series.isna() | baseline.isna()] = None 

    return regime 

# adx trend   direction

def derive_adx_trend_direction(
        adx_df: pd.DataFrame , flat_threshold_pct : float = FLAT_THRESHOLD_PCT
) -> pd.Series :

    """derive ADX trend direction : 'bullish' , 'bearish' , or 'none'."""

    if "plus_di" not in adx_df or "minus_di" not in adx_df : 
        raise ValueError("DataFrame must contain 'plus_di and 'minus_di' columns.")

    plus_di = adx_df["plus_di"]
    minus_di = adx_df["minus_di"]

    # calculating relative differnce to classify near equal value 

    di_diff_pct = ((plus_di - minus_di).abs() / pd.concat([plus_di , minus_di] , axis= 1).max(axis=1)) * 100.0

    direction = pd.Series("none" , index = adx_df.index , dtype = "object")

    direction[(plus_di > minus_di) & (di_diff_pct > flat_threshold_pct)] = "bullish"
    direction[(minus_di > plus_di) & (di_diff_pct > flat_threshold_pct)] = "bearish"
    direction[plus_di.isna() | minus_di.isna()] = None 

    return direction

def derive_adx_trend_strength(
    adx_df: pd.DataFrame,
    weak_threshold: float = ADX_WEAK_THRESHOLD,
    strong_threshold: float = ADX_STRONG_THRESHOLD,
) -> pd.Series:
    """derive ADX trend strength: 'weak', 'strong', or 'very_strong'."""
    if "adx" not in adx_df:
        raise ValueError("DataFrame must contain 'adx' column.")

    adx = adx_df["adx"]
    strength = pd.Series("strong", index=adx_df.index, dtype="object")

    strength[adx < weak_threshold] = "weak"
    strength[adx > strong_threshold] = "very_strong"
    strength[adx.isna()] = None

    return strength

# obv_trend

def derive_obv_trend(
        obv_series : pd.Series ,
        lookback : int = OBV_TREND_LOOKBACK ,
        flat_threshold_pct : float = FLAT_THRESHOLD_PCT,
) -> pd.Series :

    """derive obv multi-period slop trend : 'rising' , 'falling', or 'flat'."""

    pct_change = calculate_pct_change(obv_series  , periods = lookback)

    trend = pd.Series("flat" , index = obv_series.index , dtype = "object")

    trend[pct_change > flat_threshold_pct] = "rising"
    trend[pct_change < -flat_threshold_pct] = "falling"
    trend[obv_series.isna() | pct_change.isna() ] = None 

    return trend

#  vwap_position

def derive_vwap_position(
    close_series: pd.Series,
    vwap_series: pd.Series,
    flat_threshold_pct: float = FLAT_THRESHOLD_PCT,
) -> pd.Series:
    """Derive price relative position to VWAP: 'above', 'below', or 'at'."""
    dev_pct = ((close_series - vwap_series) / vwap_series.abs().replace(0, np.nan)) * 100.0

    position = pd.Series("at", index=close_series.index, dtype="object")
    position[dev_pct > flat_threshold_pct] = "above"
    position[dev_pct < -flat_threshold_pct] = "below"
    position[close_series.isna() | vwap_series.isna()] = None
    return position


# vwap_deviation_pct

def derive_vwap_deviation_pct(
    close_series: pd.Series, vwap_series: pd.Series
) -> pd.Series:
    """Calculate raw numeric percentage deviation from VWAP: ((close - vwap) / vwap) * 100."""
    denom = vwap_series.abs().replace(0, np.nan)
    dev_pct = ((close_series - vwap_series) / denom) * 100.0
    return dev_pct.round(4)


# stoch_status

def derive_stoch_status(
    stoch_df: pd.DataFrame,
    overbought: float = STOCH_OVERBOUGHT_THRESHOLD,
    oversold: float = STOCH_OVERSOLD_THRESHOLD,
) -> pd.Series:
    """Derive Stochastic Oscillator status: 'overbought', 'oversold', or 'neutral'."""
    if "stoch_k" not in stoch_df:
        raise ValueError("DataFrame must contain 'stoch_k' column.")

    stoch_k = stoch_df["stoch_k"]
    status = pd.Series("neutral", index=stoch_df.index, dtype="object")

    status[stoch_k > overbought] = "overbought"
    status[stoch_k < oversold] = "oversold"
    status[stoch_k.isna()] = None
    return status


# stoch_crossover
def derive_stoch_crossover(stoch_df: pd.DataFrame) -> pd.Series:
    """Derive Stochastic %K and %D crossover: 'bullish', 'bearish', or 'none'."""
    if "stoch_k" not in stoch_df or "stoch_d" not in stoch_df:
        raise ValueError("DataFrame must contain 'stoch_k' and 'stoch_d' columns.")

    k = stoch_df["stoch_k"]
    d = stoch_df["stoch_d"]

    above = k > d
    prev_above = above.shift(1)

    crossover = pd.Series("none", index=stoch_df.index, dtype="object")
    crossover[(above == True) & (prev_above == False)] = "bullish"
    crossover[(above == False) & (prev_above == True)] = "bearish"
    crossover[k.isna() | d.isna() | prev_above.isna()] = None
    return crossover

