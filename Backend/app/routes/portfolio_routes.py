
from fastapi import APIRouter , Depends , HTTPException , Response , status , Request 

from app.db.connection import get_db
from sqlalchemy.orm import Session 

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.portfolio_auth import PortfolioInfo
from app.schemas.portfolio_validation import ValidatePortfolio , PortfolioUpdate , PortfolioResponse , AssetsInfo , AssetsResponse , PortfolioSourceValidation , PortfolioSourceResponse , PortfolioSourceUpdate , FilterParams , SortFields , SortOrder
from app.security.jwtsecure import get_current_user

from app.services.portfolio_service import PortfolioServices , AssetsService

router = APIRouter(tags=["Portfolios"])

# POST /portfolio -- create
@router.post("/portfolio" , status_code= status.HTTP_201_CREATED)
async def create_portfolio( portfolio : ValidatePortfolio  , db : AsyncSession= Depends(get_db) , current_user = Depends(get_current_user)):
 

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
    
    await db.add(new_portfolio)
    await db.commit()
    await db.refresh(new_portfolio)

    return{
        "message" : "Portfolio created sucessfully "
    }


# GET /portflio -- get all portfolios for current user 

@router.get("/portfolios" , status_code=status.HTTP_200_OK)
async def getting_all_user_portfolios(db : AsyncSession = Depends(get_db) , current_user = Depends(get_current_user)):

    result =  await db.execute(select(PortfolioInfo).where(PortfolioInfo.user_id == current_user.id))
    return  result.scalars().all()
    

# GET /Portfolio/{portfolio_id} -- get specific portfolio

@router.get("/portfolio/{portfolio_id}" , status_code=status.HTTP_200_OK)
async def users_specific_portfolio( portfolio_id : int , db : AsyncSession = Depends(get_db) , current_user = Depends(get_current_user)):

    result = await db.execute(select(PortfolioInfo).where(    PortfolioInfo.portfolio_id == portfolio_id ,
        PortfolioInfo.user_id == current_user.id))
    
    portfolio =result.scalars().first()

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
    db : AsyncSession  = Depends(get_db),
    current_user = Depends(get_current_user)

):
    result = db.execute(select(PortfolioInfo).where( PortfolioInfo.portfolio_id == portfolio_id ,
        PortfolioInfo.user_id == current_user.id))
    portfolio = result.scalars().first()

    if not portfolio :
        raise HTTPException(
            status_code= 404 , detail="profile not found"
        )
    
    update_portfolio = portfolio_update.model_dump(exclude_unset=True)
    
    for field , value in update_portfolio.items():
        setattr(portfolio , field , value)

    await db.commit()
    await db.refresh(portfolio)

    return{
        "message": "Portfolio updated successfully"
    }
    
# Delete /Portfolio/{portfolio_id} -- delete / archive portfolio

@router.delete("/portfolio/{portfolio_id}" , status_code=status.HTTP_200_OK)
async def deleting_portfolio(
    portfolio_id : int , 
    db : AsyncSession = Depends(get_db) ,
    current_user = Depends(get_current_user)
):  
    result = db.execute(select(PortfolioInfo).where( PortfolioInfo.portfolio_id == portfolio_id ,
        PortfolioInfo.user_id == current_user.id))
     
    portfolio = result.scalars().first()

    if not portfolio :
        raise HTTPException(
            status_code= 404 ,detail= "portfolio not found "
        )
    
    portfolio.is_archived = True 
    await db.commit()

    return {
        "message": "Portfolio archivd successfully"
    }


# post / portfolio source  , portolio_id as parameter

@router.post("/portfolio/{portfolio_id}/sources" , status_code=status.HTTP_201_CREATED , response_model= PortfolioSourceResponse ,)
async def create_portfolio_source(
    portfolio_id : int , 
    portfolio_source  : PortfolioSourceValidation , 
    db : AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user) ,
):
    service = PortfolioServices(db)
    return await service.creating_portfolio_info(portfolio_id= portfolio_id ,data= portfolio_source)


# get portfolio source , portolio_id as paramete , all soruces

@router.get("/portfolio/{portfolio_id/sources}" , status_code=status.HTTP_200_OK , response_model=list[PortfolioSourceResponse ])
async def get_portfolio_source(
    portfolio_id : int , # sent by client via querry 
    db : AsyncSession = Depends(get_db) ,
    current_user = Depends(get_current_user) ,
):
    service =  PortfolioServices(db)
    return await service.getting_portfolio_sources(portfolio_id= portfolio_id)


#  get portfolio source , portfolio_id and source_id , specific one 
@router.get("/{portfolio_id}/source/{source_id}" , response_model= PortfolioSourceResponse)
async def get_portfolio_source(
    portfolio_id : int , 
    source_id : int , 
    db : AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = PortfolioServices(db)
    return await service.getting_portfolio_source(
        portfolio_id=portfolio_id ,
        source_id=source_id ,
        current_user=current_user
    )


# patch , portfoli source update , portfolio_id and source_id


@router.patch("/{portfolio_id}/sources/{source_id}", response_model=PortfolioSourceResponse)
async def update_portfolio_source(
    portfolio_id: int,
    source_id: int,
    data: PortfolioSourceUpdate,
    db: AsyncSession= Depends(get_db),
    current_user = Depends(get_current_user)  # Added to ensure they own it if needed
):
    service = PortfolioServices(db)
    return await service.update_portfolio_source(
        portfolio_id=portfolio_id, 
        source_id=source_id, 
        data=data
    )
# delete , portfolio source detele , portfolio_id and source_id

@router.delete("/{portfolio_id}/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio_source(
    portfolio_id: int,
    source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = PortfolioServices(db)
    service.archive_portfolio_source(portfolio_id=portfolio_id, source_id=source_id)
    return None


@router.get("/{asset_id}/" ,status_code= status.HTTP_200_OK) 
async def list_assets(
    asset_id : int , 
    db : AsyncSession = Depends(get_db) ,
    current_user = Depends(get_current_user)
):
    service = AssetsService(db)
    return await service.list_assets(
        asset_id=asset_id , 
    )

@router.get("/assets" , status_code=status.HTTP_200_OK)
async def read_assets(
    search_term : str = None , 
    filter_type : str = None ,
    sort_by : str = "name",
    sort_order : str = "asc",
    offset: int = 0 ,
    limit : int = 10 ,
    db : AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = AssetsService(db)
    return await service.get_assets(search_term , filter_type ,sort_by , sort_order , offset , limit)