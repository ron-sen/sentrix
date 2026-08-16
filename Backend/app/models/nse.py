from sqlalchemy.orm import Mapped , mapped_column , relationship
from sqlalchemy import String , Text , Integer , BigInteger ,  ForeignKey , TIMESTAMP , func , Boolean , Date , Numeric
from sqlalchemy import CheckConstraint
from sqlalchemy import UniqueConstraint
from app.db.connection import Base
from datetime import datetime
from typing import Optional


class MarketInstruments(Base):

    __tablename__ = "marketinstruments"

    instrument_id : Mapped[int] = mapped_column( Integer , primary_key=True)

    symbol : Mapped[str] = mapped_column(String(32) , nullable=False , unique=True )

    name : Mapped[str] =  mapped_column(String(120) , nullable= False)

    instrument_type : Mapped[str] = mapped_column(String(24) , nullable = False)

    exchange : Mapped[str] = mapped_column(String(16) , nullable = False , default="NSE")

    nse_symbol : Mapped[Optional[str]] = mapped_column(String(32))
    isin : Mapped[Optional[str]] = mapped_column(String(12))

    is_active : Mapped[bool] = mapped_column(Boolean , nullable=False , default= True)

    created_at : Mapped[datetime] = mapped_column(TIMESTAMP , nullable= False , server_default=func.current_timestamp())

    updated_at : Mapped[datetime] = mapped_column(TIMESTAMP ,nullable=False ,  server_default=func.current_timestamp() , onupdate=func.current_timestamp())


    __table_args__ = (
        CheckConstraint(
            "instrument_type IN('INDEX' , 'EQUITY')",name="chk_instrument_type"
        ),

        CheckConstraint(
            "exchange IN ('NSE' , 'BSE')"
        ),
    )


class NSEPriceCandles(Base):

    __tablename__ = "nsepricecandles"

    instrument_id : Mapped[int] = mapped_column(Integer , ForeignKey("marketinstruments.instrument_id"), primary_key=True , nullable=False)
    
    exchange : Mapped[str] = mapped_column(String(16) ,primary_key=True ,  default="NSE" , nullable=False)
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
            "timeframe IN('1m', '5m', '15m', '1h', '1d')",name= "chk_timeframe"
        ),
    )


class MarketBreadth(Base):

    __tablename__ = "market_breadth" 

    breadth_id : Mapped[int] = mapped_column(Integer , primary_key=True)

    exchange : Mapped[str] = mapped_column(String(16) , nullable=False)

    session_date : Mapped[datetime] = mapped_column(Date , nullable= False)

    advances : Mapped[int] = mapped_column(Integer)
    declines : Mapped[int] = mapped_column(Integer)
    unchanged : Mapped[int] = mapped_column(Integer)
    total : Mapped[int] = mapped_column(Integer)

    advance_decline_ratio : Mapped[float] = mapped_column(Numeric(10 , 4))

    put_call_ratio : Mapped[float] = mapped_column(Numeric(10 , 4 )) 

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)


    __table_args__ = (
    CheckConstraint("exchange IN ('NSE', 'BSE')", name="chk_breadth_exchange"),
    UniqueConstraint("exchange", "session_date", name="uq_breadth_exchange_date"),
)