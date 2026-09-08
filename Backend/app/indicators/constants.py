
"""
constants and defaults for technical indicator calculations

"""

# simple moving averages (SMA)
DEFAULT_SMA_PERIOD : int = 20 

# exponential moving average ( EMA)
DEFAULT_EMA_PERIOD : int = 20 

# relative strength index (RSI)
DEFAULT_RSI_PERIOD : int = 14
RSI_OVERSOLD_THRESHOLD :float = 30.0
RSI_OVERBOUGHT_THRESHOLD :float = 70.0

# moving average convergence divergence (MACD)
DEFAULT_MACD_FAST : int = 12 
DEFAULT_MACD_SLOW : int = 26 
DEFAULT_MACD_SIGNAL : int = 9 

# bollinger bands 
DEFAULT_BB_PERIOD : int = 20 
DEFAULT_BB_STD_DEV : float = 2.0
BB_SQUEEZE_LOOKBACK : int = 100 
BB_SQUEEZE_PERCENTILE : float = 10.0 # bttom 10% of recent bandwidth values 

# average true range (ATR)
DEFAULT_ATR_PERIOD : int = 14
ATR_BASELINE_PERIOD : int = 20 
ATR_HIGH_MULTIPLIER : float = 1.5
ATR_LOW_MULTIPLIER : float = 0.5

# average directional index (ADX)
DEFAULT_ADX_PERIOD : int = 14 
ADX_WEAK_THRESHOLD : float = 20.0
ADX_STRONG_THRESHOLD : float = 40.0

#OBV trend window 
OBV_TREND_LOOKBACK : int = 5

# stochastic oscillator 
DEFAULT_STOCH_K_PERIOD : int = 14
DEFAULT_STOCH_D_PERIOD : int = 3 
STOCH_OVERSOLD_THRESHOLD : float = 20.0
STOCH_OVERBOUGHT_THRESHOLD : float = 80.0

FLAT_THRESHOLD_PCT: float = 0.05
