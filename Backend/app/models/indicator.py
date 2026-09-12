
from sqlalchemy.orm import Mapped , mapped_column , relationship
from sqlalchemy import String , Text , Integer , BigInteger ,  ForeignKey , TIMESTAMP , func , Boolean , Date , Numeric
from sqlalchemy import CheckConstraint
from app.db.connection import Base
from datetime import datetime
from typing import Optional


class IndicatorValues(Base):

    __tablename__ = "indicator_values"

    asset_id : Mapped[int] = mapped_column(BigInteger , ForeignKey("assets.asset_id") , primary_key=True , nullable=False)

    timestamp : Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True) , primary_key= True , nullable=False )

    # moving averages
    sma :  Mapped[float] = mapped_column(Numeric , nullable= False)
    ema : Mapped[float] = mapped_column(Numeric , nullable= False)

    # strength index
    rsi : Mapped[float] = mapped_column(Numeric, nullable= False)

    # moving average convergence  , divergence 
    macd_line : Mapped[float] = mapped_column(Numeric , nullable= False)
    macd_signal : Mapped[float] = mapped_column(Numeric , nullable= False)
    macd_hist : Mapped[float] = mapped_column(Numeric, nullable= False)
    ppo: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

    # bollinger band 
    
    bb_upper : Mapped[float] = mapped_column(Numeric , nullable= False)
    bb_middle : Mapped[float] = mapped_column(Numeric , nullable= False)
    bb_lower : Mapped[float] = mapped_column(Numeric , nullable= False)
    bb_percent_b : Mapped[float] = mapped_column(Numeric, nullable= False)
    bb_bandwidth : Mapped[float] = mapped_column(Numeric , nullable= False)

    # average true range 

    atr : Mapped[float] = mapped_column(Numeric , nullable= False)

    # average directional index 

    adx : Mapped[float] = mapped_column(Numeric, nullable= False)
    plus_di : Mapped[float] = mapped_column(Numeric , nullable= False)
    minus_di :Mapped[float] = mapped_column(Numeric , nullable= False)

    # On balance Volume 

    obv : Mapped[int] = mapped_column(BigInteger, nullable= False)

    # volume weighted average price

    vwap : Mapped[float] = mapped_column(Numeric , nullable= False)

    # stochastic oscillator 

    stoch_k : Mapped[float] = mapped_column(Numeric, nullable= False)
    stoch_d : Mapped[float] = mapped_column(Numeric , nullable= False)

    __table_args__ = (
    CheckConstraint("rsi >= 0 AND rsi <= 100", name="ck_rsi_range"),
    CheckConstraint("adx >= 0 AND adx <= 100", name="ck_adx_range"),
    CheckConstraint("plus_di >= 0 AND plus_di <= 100", name="ck_plus_di_range"),
    CheckConstraint("minus_di >= 0 AND minus_di <= 100", name="ck_minus_di_range"),
    CheckConstraint("stoch_k >= 0 AND stoch_k <= 100", name="ck_stoch_k_range"),
    CheckConstraint("stoch_d >= 0 AND stoch_d <= 100", name="ck_stoch_d_range"),
)


class IndicatorSignal(Base):

    __tablename__ = "indicator_signals"

    asset_id : Mapped[int] = mapped_column(BigInteger , ForeignKey("assets.asset_id") , primary_key= True , nullable=False)

    timestamp : Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True) , primary_key=True , nullable=False)

    sma_slope : Mapped[str] = mapped_column(String(10) , nullable= False)
    ema_slope : Mapped[str] = mapped_column(String(10) , nullable= False)
    rsi_status : Mapped[str] = mapped_column(String(15) , nullable= False)

    macd_crossover : Mapped[str] = mapped_column(String(10) , nullable= False)
    macd_hist_direction  : Mapped[str] = mapped_column(String(15) , nullable= False)
    bb_status : Mapped[str] = mapped_column(String(10) , nullable=False)
    atr_vol_regime : Mapped[str] = mapped_column(String(10) , nullable= False)
    adx_trend_strength :  Mapped[str] = mapped_column(String(15) , nullable= False)
    adx_trend_direction : Mapped[str] = mapped_column(String(15) , nullable= False)
    obv_trend : Mapped[str] = mapped_column(String(15) , nullable= False)
    vwap_position :  Mapped[str] = mapped_column(String(15) , nullable= False)
    vwap_deviation_pct : Mapped[float] = mapped_column(Numeric , nullable= False)
    stoch_status : Mapped[str] = mapped_column(String(15) , nullable= False)
    stoch_crossover :  Mapped[str] = mapped_column(String(15) , nullable= False)

    __table_args__ = (
        CheckConstraint("sma_slope IN ('rising','falling','flat')", name="ck_sma_slope"),

        CheckConstraint("ema_slope IN ('rising','falling','flat')", name="ck_ema_slope"),

        CheckConstraint("rsi_status IN ('overbought','oversold','neutral')", name="ck_rsi_status"),

        CheckConstraint("macd_crossover IN ('bullish','bearish','none')", name="ck_macd_crossover"),

        CheckConstraint("macd_hist_direction IN ('expanding','contracting','flat')", name="ck_macd_hist_dir"),

        CheckConstraint("bb_status IN ('overbought','oversold','squeeze','normal')", name="ck_bb_status"),

        CheckConstraint("atr_vol_regime IN ('high','low','normal')", name="ck_atr_vol_regime"),

        CheckConstraint("adx_trend_strength IN ('weak','strong','very_strong')", name="ck_adx_strength"),

        CheckConstraint("adx_trend_direction IN ('bullish','bearish','none')", name="ck_adx_direction"),

        CheckConstraint("obv_trend IN ('rising','falling','flat')", name="ck_obv_trend"),

        CheckConstraint("vwap_position IN ('above','below','at')", name="ck_vwap_position"),

        CheckConstraint("stoch_status IN ('overbought','oversold','neutral')", name="ck_stoch_status"),

        CheckConstraint("stoch_crossover IN ('bullish','bearish','none')", name="ck_stoch_crossover"),

    )


class SuitabilityScores(Base) :

    __tablename__ = "suitability_scores"

    asset_id : Mapped[int] = mapped_column(BigInteger , ForeignKey("assets.asset_id") , primary_key= True , nullable=False)
    
    timestamp : Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True) , primary_key=True , nullable=False)

    suitability_score : Mapped[float] = mapped_column(Numeric , nullable=False)

    rsi_input : Mapped[float] = mapped_column(Numeric , nullable=False)

    ppo_input : Mapped[float] = mapped_column(Numeric , nullable=False)

    atr_input : Mapped[float] = mapped_column(Numeric , nullable=False)

    __table_args__ = (
        CheckConstraint("suitability_score >= 0 AND suitability_score <= 100", name="ck_suitability_range"),
    )