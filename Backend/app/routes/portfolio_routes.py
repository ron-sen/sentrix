
from fastapi import APIRouter , Depends , HTTPException , Response , status , Request 

from app.db.connection import get_db
from sqlalchemy.orm import Session 

from app.models.portfolio_auth import PortfolioInfo
from app.schemas.portfolio_validation import ValidatePortfolio , PortfolioUpdate , PortfolioResponse
from app.security.jwtsecure import get_current_user

router = APIRouter()

# POST /portfolio -- create
@router.post("/portfolio" , status_code= status.HTTP_201_CREATED)
async def create_portfolio( portfolio : ValidatePortfolio  , db : Session = Depends(get_db) , current_user = Depends(get_current_user)):
 

    new_portfolio = PortfolioInfo(
            
            user_id = current_user.id ,
            portfolio_name = portfolio.portfolio_name ,
            base_currency = portfolio.base_currency , 
            risk_tolerance = portfolio.risk_tolerance ,
            liquidity_needs = portfolio.liquidity_needs,
            investment_horizon = portfolio.investment_horizon , 
            rebalance_frequency = portfolio.rebalance_frequency ,
            is_default = portfolio.is_default 
        )
    
    db.add(new_portfolio)
    db.commit()
    db.refresh(new_portfolio)

    return{
        "message" : "Portfolio created sucessfully "
    }


# GET /portflio -- get all portfolios for current user 

@router.get("/portfolios" , status_code=status.HTTP_200_OK)
async def getting_all_user_portfolios(db : Session = Depends(get_db) , current_user = Depends(get_current_user)):

    return  db.query(PortfolioInfo).filter(PortfolioInfo.user_id == current_user.id).all()
    

# GET /Portfolio/{portfolio_id} -- get specific portfolio

@router.get("/portfolio/{portfolio_id}" , status_code=status.HTTP_200_OK)
async def users_specific_portfolio( portfolio_id : int , db : Session = Depends(get_db) , current_user = Depends(get_current_user)):

    portfolio = db.query(PortfolioInfo).filter(

        PortfolioInfo.portfolio_id == portfolio_id ,
        PortfolioInfo.user_id == current_user.id

    ).first()

    if not portfolio :
        raise HTTPException(
            status_code = 404 ,detail="Portfolio not found "
        )

    return portfolio


# PATCH /Portfolio{portfolio_id} -- update portfolio

@router.patch("/portfolio/{portfolio_id}" , status_code=status.HTTP_200_OK)
async def update_user_portfolio(
    portfolio_id : int , 
    portfolio_update : PortfolioUpdate ,
    db : Session  = Depends(get_db),
    current_user = Depends(get_current_user)

):
    
    portfolio = db.query(PortfolioInfo).filter(

        PortfolioInfo.portfolio_id == portfolio_id ,
        PortfolioInfo.user_id == current_user.id
        
    ).first()

    if not portfolio :
        raise HTTPException(
            status_code= 404 , detail="profile not found"
        )
    
    update_portfolio = portfolio_update.model_dump(exclude_unset=True)
    
    for field , value in update_portfolio.items():
        setattr(portfolio , field , value)

    db.commit()
    db.refresh(portfolio)

    return{
        "message": "Portfolio updated successfully"
    }
    
# Delete /Portfolio/{portfolio_id} -- delete / archive portfolio

@router.delete("/portfolio/{portfolio_id}" , status_code=status.HTTP_200_OK)
async def deleting_portfolio(
    portfolio_id : int , 
    db : Session = Depends(get_db) ,
    current_user = Depends(get_current_user)
):
    portfolio  = db.query(PortfolioInfo).filter(

        PortfolioInfo.portfolio_id == portfolio_id ,
        PortfolioInfo.user_id == current_user.id
    ).first()
    if not portfolio :
        raise HTTPException(
            status_code= 404 ,detail= "portfolio not found "
        )
    
    portfolio.is_archived = True 
    db.commit()

    return {
        "message": "Portfolio archivd successfully"
    }