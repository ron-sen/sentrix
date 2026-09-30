
"""
engine layer for fetching candles , cleaning time series-data  , driving calculations/signals 
and persisting output to the database.

Orchestrates the indicator pipeline for a single asset:
fetch candles -> sanitize -> calculate -> derive signals -> upsert to DB.
This is the only file in app/indicators/ that touches the database.
"""

import logging
from typing import List , Optional 
import numpy as np 
import pandas as pd

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
 
from app.ml.indicators import calculations as calc
from app.ml.indicators import signals as sig
from app.ml.indicators.constants import (
    DEFAULT_ADX_PERIOD,
    DEFAULT_ATR_PERIOD,
    DEFAULT_BB_PERIOD,
    DEFAULT_EMA_PERIOD,
    DEFAULT_MACD_FAST,
    DEFAULT_MACD_SIGNAL,
    DEFAULT_MACD_SLOW,
    DEFAULT_RSI_PERIOD,
    DEFAULT_SMA_PERIOD,
    DEFAULT_STOCH_D_PERIOD,
    DEFAULT_STOCH_K_PERIOD,
    PPO_FAST_PERIOD,
    PPO_SLOW_PERIOD,
)

MIN_WARMUP_BARS = 100  # inside engine.py / celery pipline task
# import our db  orm models 

from app.models.indicator import IndicatorSignal , IndicatorValues 
from app.models.portfolio_auth import MarketPriceCandles

logger = logging.getLogger(__name__)

def sanitize_ohlcv_dataframe( df : pd.DataFrame , freq : str = "1min") -> pd.DataFrame :
    """
    Reindexes OHLCV Dataframe to continuous time index , forward-fills gaps ,and handles zero-volume missing periods 

    """

    if df.empty:
        return df

    # ensuring index is datetime sorted 

    df = df.sort_index()

    # reindexing to a complete datetime grid to detect missing time  intervals

    full_index = pd.date_range(start= df.index.min() , end = df.index.max() , freq = freq , tz = df.index.tz)
    resampled = df.reindex(full_index)


    # impute open , high , low , with close if missing 

    resampled["close"] = resampled["close"].ffill().bfill()

    resampled["open"] = resampled["open"].fillna(resampled["close"])
    resampled["high"] = resampled["high"].fillna(resampled["close"])
    resampled["low"] = resampled["low"].fillna(resampled["close"])

    # fill missing volume with 0.0 
    if "volume" in resampled.columns :
        resampled["volume"] = resampled["volume"].fillna(0.0)

    return resampled

class IndicatorEngine : 

    """ orchestrates candle retrieval  , data cleaning , indicator calculation , signal derivation , and DB presistence per asset. """

    def __init__(self, db_session: AsyncSession, lookback_bars: int = 1440):
        self.db = db_session
        self.lookback_bars = lookback_bars

    async def fetch_ohlcv(self , asset_id : int , exchange : str = "AGGREAGATED" , timeframe: str = "1m") -> pd.DataFrame:
        """
        Fetch raw candles from DB and load into  a pandas dataframe
        """

        stmt = (
           select(MarketPriceCandles).where(
                MarketPriceCandles.asset_id == asset_id ,
                MarketPriceCandles.exchange == exchange ,
                MarketPriceCandles.timeframe == timeframe ,
           ).order_by(MarketPriceCandles.candle_time.desc()).limit(self.lookback_bars)
        )
        result = await self.db.execute(stmt)
        candles = result.scalars().all()

        if not candles :
            return pd.DataFrame()

        record = [
            {
                "timestamp" : c.candle_time ,
                "open" : float(c.open_price),
                "high" : float(c.high_price),
                "low" : float(c.low_price),
                "close" : float(c.close_price),
                "volume" : float(c.volume) if c.volume is not None else 0.0 ,
            }
            for c in candles
        ]

        df = pd.DataFrame(record)
        df.set_index("timestamp" , inplace=True)
        return df.sort_index()

    async def process_asset(
            self , asset_id : int , exchange : str = "AGGREGATED" , timeframe : str = "1m" , freq: str = "1min"
    )-> None :

        """ run complete pipline for a given asset
        fetch -> sanitize -> calculate -> derive signals -> prersist db
        """

        raw_df = await self.fetch_ohlcv(asset_id=asset_id , exchange=exchange , timeframe=timeframe)
        if raw_df.empty:
            logger.warning(f"No OHLCV data found for asset_id = {asset_id} , exchange = {exchange} , timeframe = {timeframe}")
            return 

        df = sanitize_ohlcv_dataframe(raw_df, freq=freq)

        # --- Calculations ---
        sma_series = calc.calculate_sma(df["close"], period=DEFAULT_SMA_PERIOD)
        ema_series = calc.calculate_ema(df["close"], period=DEFAULT_EMA_PERIOD)
        rsi_series = calc.calculate_rsi(df["close"], period=DEFAULT_RSI_PERIOD)
        ppo_series = calc.calculate_ppo(df["close"], fast_period=PPO_FAST_PERIOD, slow_period=PPO_SLOW_PERIOD)

        macd_df = calc.calculate_macd(
            df["close"],
            fast_period=DEFAULT_MACD_FAST,
            slow_period=DEFAULT_MACD_SLOW,
            signal_period=DEFAULT_MACD_SIGNAL,
        )
        bb_df = calc.calculate_bollinger_bands(df["close"], period=DEFAULT_BB_PERIOD)
        atr_series = calc.calculate_atr(df, period=DEFAULT_ATR_PERIOD)
        adx_df = calc.calculate_adx(df, period=DEFAULT_ADX_PERIOD)
        stoch_df = calc.calculate_stochastic(
            df, k_period=DEFAULT_STOCH_K_PERIOD, d_period=DEFAULT_STOCH_D_PERIOD
        )
        obv_series = calc.calculate_obv(df)
        vwap_series = calc.calculate_vwap(df)

        # --- Signals ---
        sma_slope = sig.derive_sma_slope(sma_series)
        ema_slope = sig.derive_ema_slope(ema_series)
        rsi_status = sig.derive_rsi_status(rsi_series)
        macd_crossover = sig.derive_macd_crossover(macd_df)
        macd_hist_dir = sig.derive_macd_hist_direction(macd_df)
        bb_status = sig.derive_bb_status(df["close"], bb_df)
        atr_vol_regime = sig.derive_atr_vol_regime(atr_series)
        adx_strength = sig.derive_adx_trend_strength(adx_df)
        adx_direction = sig.derive_adx_trend_direction(adx_df)
        obv_trend = sig.derive_obv_trend(obv_series)
        vwap_pos = sig.derive_vwap_position(df["close"], vwap_series)
        vwap_dev_pct = sig.derive_vwap_deviation_pct(df["close"], vwap_series)
        stoch_status = sig.derive_stoch_status(stoch_df)
        stoch_crossover = sig.derive_stoch_crossover(stoch_df)

        latest_idx = df.index[-1]

        values_payload = {
            "asset_id": asset_id,
            "timestamp": latest_idx,
            "sma": self._safe_float(sma_series.loc[latest_idx]),
            "ema": self._safe_float(ema_series.loc[latest_idx]),
            "rsi": self._safe_float(rsi_series.loc[latest_idx]),
            "macd_line": self._safe_float(macd_df["macd"].loc[latest_idx]),
            "macd_signal": self._safe_float(macd_df["macd_signal"].loc[latest_idx]),
            "macd_hist": self._safe_float(macd_df["macd_hist"].loc[latest_idx]),

            "ppo": self._safe_float(ppo_series.loc[latest_idx]) ,

            "bb_upper": self._safe_float(bb_df["bb_upper"].loc[latest_idx]),
            "bb_middle": self._safe_float(bb_df["bb_middle"].loc[latest_idx]),
            "bb_lower": self._safe_float(bb_df["bb_lower"].loc[latest_idx]),
            "bb_percent_b": self._safe_float(bb_df["bb_percent_b"].loc[latest_idx]),
            "bb_bandwidth": self._safe_float(bb_df["bb_bandwidth"].loc[latest_idx]),
            "atr": self._safe_float(atr_series.loc[latest_idx]),
            "adx": self._safe_float(adx_df["adx"].loc[latest_idx]),
            "plus_di": self._safe_float(adx_df["plus_di"].loc[latest_idx]),
            "minus_di": self._safe_float(adx_df["minus_di"].loc[latest_idx]),
            "obv": self._safe_float(obv_series.loc[latest_idx]),
            "vwap": self._safe_float(vwap_series.loc[latest_idx]),
            "stoch_k": self._safe_float(stoch_df["stoch_k"].loc[latest_idx]),
            "stoch_d": self._safe_float(stoch_df["stoch_d"].loc[latest_idx]),
        }

        signals_payload = {
            "asset_id": asset_id,
            "timestamp": latest_idx,
            "sma_slope": sma_slope.loc[latest_idx],
            "ema_slope": ema_slope.loc[latest_idx],
            "rsi_status": rsi_status.loc[latest_idx],
            "macd_crossover": macd_crossover.loc[latest_idx],
            "macd_hist_direction": macd_hist_dir.loc[latest_idx],
            "bb_status": bb_status.loc[latest_idx],
            "atr_vol_regime": atr_vol_regime.loc[latest_idx],
            "adx_trend_strength": adx_strength.loc[latest_idx],
            "adx_trend_direction": adx_direction.loc[latest_idx],
            "obv_trend": obv_trend.loc[latest_idx],
            "vwap_position": vwap_pos.loc[latest_idx],
            "vwap_deviation_pct": self._safe_float(vwap_dev_pct.loc[latest_idx]),
            "stoch_status": stoch_status.loc[latest_idx],
            "stoch_crossover": stoch_crossover.loc[latest_idx],
        }

        await self._upsert(IndicatorValues, values_payload)
        await self._upsert(IndicatorSignal, signals_payload)
        await self.db.commit()

    async def _upsert(self, model_class, payload: dict) -> None:
        
        """Executes a PostgreSQL ON CONFLICT DO UPDATE upsert on (asset_id, timestamp)."""

        stmt = insert(model_class).values(**payload)
        update_dict = {k: v for k, v in payload.items() if k not in ("asset_id", "timestamp")}

        on_conflict_stmt = stmt.on_conflict_do_update(
            index_elements=["asset_id", "timestamp"], set_=update_dict
        )
        await self.db.execute(on_conflict_stmt)

    # new improvision : enfore gap detectiona
    async def process_asset_with_gap_detection(self , asset_id : int , exchange : str  = "AGGREGATED" , timeframe : str = "1m"):

        df = await self.fetch_ohlcv(asset_id = asset_id , exchange = exchange , timeframe = timeframe)

        if len(df) < MIN_WARMUP_BARS : 
            logger.warning(f"Asset {asset_id} has insufficient historical candles ({len(df)}/{MIN_WARMUP_BARS}). Skipping signal generation until warm.")

        # check for timestamp continuity on the most recent 30 bars

        recent_timestamp = df.index[-30:]
        time_diffs = recent_timestamp.to_series().diff()

        if (time_diffs > pd.Timedelta(minutes = 2 )).any():
            logger.error(f"Timestamp gap detected in recent candles for asset { asset_id} , Triggering REST API backfill...")
            # Trigger historical REST backfill service here before  calcultating signals 

            # proceed to indicator and fuzzy suitability calculations safely 
            await self.process_asset(asset_id= asset_id , exchange= exchange , timeframe= timeframe)


    @staticmethod
    def _safe_float(val) -> Optional[float]:
        """Convert scalar value to float safely, or None if NaN/Inf."""
        if pd.isna(val) or np.isinf(val):
            return None
        return float(val)
        