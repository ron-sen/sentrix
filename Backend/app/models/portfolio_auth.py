
from sqlalchemy.orm import Mapped , mapped_column , relationship
from sqlalchemy import String , Text , Integer , ForeignKey , TIMESTAMP , func , Boolean , Date , Numeric
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

    network : Optional[str] = mapped_column(String(80))
    contract_address : Optional[str] = mapped_column(String(128))
    coingecko_id : Optional[str] = mapped_column(String(120))
    cmc_id : Optional[str] = mapped_column(String(120))
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
    account_label : Optional[str] = mapped_column(String(100))

    wallet_address : Optional[str] = mapped_column(String(160))
    network : Optional[str] = mapped_column(String(80))

    external_account_id : Optional[str] = mapped_column(String(160))

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

