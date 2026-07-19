
from sqlalchemy.orm import Mapped , mapped_column , relationship
from sqlalchemy import String , Text , Integer , BigInteger ,  ForeignKey , TIMESTAMP , func , Boolean , Date , Numeric
from sqlalchemy import CheckConstraint
from app.db.connection import Base
from datetime import datetime
from typing import Optional

class PortfolioInfo(Base):

    __tablename__ = "portfolios"

    portfolio_id : Mapped[int] = mapped_column(primary_key=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False )
    portfolio_name : Mapped[str] = mapped_column(String(100) , nullable=False)
    base_currency : Mapped[str] = mapped_column(String(12) , nullable=False , default="USD")
    risk_tolerance : Mapped[str] = mapped_column(String(20), nullable=False , default="MODERATE")
    liquidity_needs : Mapped[str] = mapped_column(String(20) , nullable=False , default="MEDIUM")
    investment_horizon : Mapped[str] = mapped_column(String(20) , nullable=False , default="MID_TERM")

    target_volatility_pct : Mapped[float] = mapped_column(Numeric(6,3), nullable=True)

    max_asset_weight_pct : Mapped[float] = mapped_column(Numeric(6,3) , nullable=True)

    rebalance_frequency : Mapped[str] = mapped_column(String(20) , nullable=False , default="MANUAL") 

    is_default : Mapped[bool]= mapped_column(Boolean , nullable=False, default= False)

    is_archived : Mapped[bool] = mapped_column(Boolean , nullable=False , default=False)

    created_at : Mapped[datetime]= mapped_column(TIMESTAMP ,nullable=False , server_default=func.current_timestamp() )

    updated_at : Mapped[datetime] = mapped_column(TIMESTAMP ,nullable=False ,  server_default=func.current_timestamp() , onupdate=func.current_timestamp())


    __table_args__ = (
        CheckConstraint(
            "risk_tolerance IN ('CONSERVATIVE' , 'MODERATE' ,'AGGRESSIVE' )" , name="chk_risk_tolerance"
        ),

        CheckConstraint(
            "liquidity_needs IN ('LOW', 'MEDIUM', 'HIGH')",name = "chk_liquidity_needs"
        ),

        CheckConstraint(
            "investment_horizon IN ('SHORT_TERM', 'MID_TERM', 'LONG_TERM')",name ="chk_investment_horizon"
        ),

        CheckConstraint(
            "rebalance_frequency IN ('MANUAL', 'DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY')",name = "chk_rebalance_frequency"

        )
    )

    user = relationship("User", back_populates="portfolios")


class Assets(Base):

    __tablename__ = "assets"

    asset_id : Mapped[int] = mapped_column(Integer , primary_key=True)
    symbol : Mapped[str] = mapped_column(String(32) , nullable=False)
    name : Mapped[str] = mapped_column(String(120) , nullable=False)

    asset_type : Mapped[str] = mapped_column(String(24) , nullable=False , default="CRYPTO")

    network: Mapped[Optional[str]] = mapped_column(String(80))
    contract_address: Mapped[Optional[str]] = mapped_column(String(128))
    coingecko_id: Mapped[Optional[str]] = mapped_column(String(120))
    cmc_id: Mapped[Optional[str]] = mapped_column(String(120))
    # polygon
    polygon_ticker : Mapped[Optional[str]] = mapped_column(String(32))
    binance_symbol: Mapped[Optional[str]] = mapped_column(String(32))
    
    decimals : Mapped[int] = mapped_column(Integer , nullable=False , default=18)
    is_active : Mapped[bool] = mapped_column(Boolean , nullable=False  , default=True)

    created_at : Mapped[datetime] = mapped_column(TIMESTAMP , nullable= False , server_default=func.current_timestamp())

    updated_at : Mapped[datetime] = mapped_column(TIMESTAMP  , nullable=False , server_default=func.current_timestamp())

    __table_args__= (

        CheckConstraint(
            "asset_type IN ( 'CRYPTO', 'STABLECOIN', 'FIAT', 'TOKENIZED_ASSET')",name="chk_asset_type"
        ),
        CheckConstraint(
            "decimals BETWEEN 0 AND 36", name="chk_decimals"
        )

    )

class PortfolioSources(Base):

    __tablename__ ="portfolio_sources"

    source_id : Mapped[int] = mapped_column(Integer , primary_key=True)
    portfolio_id : Mapped[int] = mapped_column(ForeignKey("portfolios.portfolio_id" , ondelete="CASCADE"))

    source_type : Mapped[str] = mapped_column(String(24) , nullable=False)

    provider_name : Mapped[str] = mapped_column(String(80) , nullable=False)
    account_label : Mapped[Optional[str]] = mapped_column(String(100))

    wallet_address : Mapped[Optional[str]] = mapped_column(String(160))
    network : Mapped[Optional[str]] = mapped_column(String(80))

    external_account_id : Mapped[Optional[str]] = mapped_column(String(160))

    sync_status : Mapped[str] = mapped_column(String(24) , nullable=False , default="NOT_CONNECTED")


    last_synced_at : Mapped[datetime] = mapped_column(TIMESTAMP , server_default=func.current_timestamp())

    created_at : Mapped[datetime] = mapped_column(TIMESTAMP , nullable=False  ,  server_default=func.current_timestamp())

    updated_at : Mapped[datetime] = mapped_column(TIMESTAMP , nullable=False , server_default=func.current_timestamp())


    __table_args__ = (
        CheckConstraint(
            "source_type IN ('EXCHANGE', 'WALLET', 'MANUAL', 'CUSTODIAN')",name="chk_source_type"
        ),

        CheckConstraint(
            "sync_status IN ('NOT_CONNECTED', 'ACTIVE', 'PAUSED', 'ERROR')",
            name="chk_sync_status"
        )
    )


class PortfolioTransactions(Base):

    __tablename__ = "portfolio_transactions"

    transaction_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolios.portfolio_id", ondelete="CASCADE"), nullable=False)
    source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("portfolio_sources.source_id", ondelete="SET NULL"))
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.asset_id"), nullable=False)

    transaction_type: Mapped[str] = mapped_column(String(24), nullable=False)

    quantity: Mapped[float] = mapped_column(Numeric(38, 18), nullable=False)
    price_per_unit: Mapped[Optional[float]] = mapped_column(Numeric(28, 10))
    fee_quantity: Mapped[float] = mapped_column(Numeric(38, 18), default=0, nullable=False)
    fee_asset_id: Mapped[Optional[int]] = mapped_column(ForeignKey("assets.asset_id"))
    total_value: Mapped[Optional[float]] = mapped_column(Numeric(28, 10))

    currency: Mapped[str] = mapped_column(String(12), default="USD", nullable=False)

    executed_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    external_tx_id: Mapped[Optional[str]] = mapped_column(String(180))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('BUY', 'SELL', 'DEPOSIT', 'WITHDRAWAL', 'TRANSFER_IN', 'TRANSFER_OUT', 'FEE', 'REWARD', 'AIRDROP', 'ADJUSTMENT')",
            name="chk_transaction_type"
        ),
        CheckConstraint("quantity <> 0", name="chk_quantity"),
        CheckConstraint("fee_quantity >= 0", name="chk_fee_quantity"),
    )


class PortfolioPosition(Base):

    __tablename__ = "portfolio_positions"

    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolios.portfolio_id", ondelete="CASCADE"), primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.asset_id"), primary_key=True)

    quantity: Mapped[float] = mapped_column(Numeric(38, 18), default=0, nullable=False)
    avg_cost_basis: Mapped[Optional[float]] = mapped_column(Numeric(28, 10))
    realized_pnl: Mapped[float] = mapped_column(Numeric(28, 10), default=0, nullable=False)
    first_acquired_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)



class MarketPriceCandles(Base):

    __tablename__ = "market_price_candles"

    asset_id : Mapped[int] = mapped_column(BigInteger , ForeignKey("assets.asset_id"), primary_key=True , nullable=False)
    exchange : Mapped[str] = mapped_column(String(80) ,primary_key=True ,  default="AGGREGATED" , nullable=False)
    timeframe : Mapped[str] = mapped_column(String(12) ,primary_key=True ,  nullable=False)
    candle_time : Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True) , primary_key=True ,  nullable=False)

    open_price : Mapped[float] = mapped_column(Numeric(28 , 10) , nullable=False)
    close_price : Mapped[float] = mapped_column(Numeric(28 , 10) , nullable=False)
    high_price : Mapped[float] = mapped_column(Numeric(28 , 10) , nullable=False)
    low_price : Mapped[float] = mapped_column(Numeric(28 , 10) , nullable=False)

    volume : Mapped[Optional[float]] = mapped_column(Numeric(38 , 18))
    quote_volume : Mapped[Optional[float]] = mapped_column(Numeric(38 , 10))
    created_at : Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True) ,nullable=False ,  server_default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint(
            "timeframe IN('1m', '5m', '15m', '1h', '4h', '1d')",name= "chk_timeframe"
        ),
    )