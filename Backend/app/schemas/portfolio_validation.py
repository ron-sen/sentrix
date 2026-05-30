
from pydantic import BaseModel  , Field , field_validator , computed_field , ConfigDict
from typing import Annotated , Optional  , Literal 
from datetime import date , datetime

class ValidatePortfolio(BaseModel):

    portfolio_name : Annotated[str ,Field(..., description= "Name for your Portfolio" , min_length=3 , max_length=100)]

    base_currency : Annotated[str , Field(... , description="Choose currency" , min_length=1 , max_length=12)]

    risk_tolerance: Literal['CONSERVATIVE', 'MODERATE', 'AGGRESSIVE'] = 'MODERATE'

    liquidity_needs : Literal['LOW', 'MEDIUM', 'HIGH'] = 'MEDIUM'

    investment_horizon : Literal['SHORT_TERM', 'MID_TERM', 'LONG_TERM'] = 'MID_TERM'

    rebalance_frequency : Literal['MANUAL', 'DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY'] = 'MANUAL'

    is_default : bool = False

class PortfolioResponse(BaseModel):

    portfolio_id : int
    user_id : int
    portfolio_name : str
    base_currency : str
    risk_tolerance : str
    liquidity_needs : str
    investment_horizon : str 
    rebalance_frequency : str
    is_default : bool
    is_archived : bool
    target_volatility_pct : Optional[float]
    max_asset_weight_pct : Optional[float]
    created_at : datetime
    updated_at : datetime 

    model_config = ConfigDict(from_attributes= True)

   


class PortfolioUpdate(BaseModel):

    
    portfolio_name : Optional[str] = Field(None ,  min_length=3 , max_length=100)

    base_currency : Optional[str] = Field(None , min_length=1 , max_length=12)

    risk_tolerance : Optional[ Literal['CONSERVATIVE', 'MODERATE', 'AGGRESSIVE']] = None

    liquidity_needs : Optional[Literal['LOW', 'MEDIUM', 'HIGH']] = None

    investment_horizon : Optional[Literal['SHORT_TERM', 'MID_TERM', 'LONG_TERM']] = None

    rebalance_frequency : Optional[Literal['MANUAL', 'DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY']] = None



   
