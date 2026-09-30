
from datetime import datetime 
from pydantic import BaseModel

class IndicatorValueResponse(BaseModel):

    timestamp : datetime
    sma: float | None 
    ema: float | None 
    rsi: float | None 
    ppo: float | None 
    atr: float | None 
    macd_line: float | None 
    macd_signal: float | None 

    class Config :
        from_attribute = True

class SuitabilityResponse(BaseModel):

    timestamp : datetime
    suitability_score : float 
    rsi_output : float
    ppo_input: float
    atr_input : float

    class Config:
        from_attributes = True


