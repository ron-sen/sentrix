
# it handles the error related to db conflict 

from sqlalchemy.exc import IntegrityError 
from sqlalchemy.orm import Session
from app.db.connection import get_db
from fastapi import Depends
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.portfolio_auth import PortfolioInfo  ,Assets , PortfolioSources
from app.schemas.portfolio_validation import ValidatePortfolio , PortfolioResponse ,PortfolioUpdate  , AssetsInfo , AssetsResponse , PortfolioSourceValidation , PortfolioSourceResponse , PortfolioSourceUpdate , FilterParams , SortOrder , SortFields

from app.security.jwtsecure import get_current_user

from app.services.exception import PortfolioSourceConflict , PortfolioSourceNotFound,NoContent , AssetNotFound


class PortfolioServices :

    async def __init__(self , db : AsyncSession):
        self.db = db

    # post / portfolio source  , portolio_id as parameter
    async def creating_portfolio_info(self , portfolio_id : int , data : PortfolioSourceValidation):
        source = PortfolioSources(

            portfolio_id = portfolio_id , 
            source_type = data.source_type ,
            provider_name = data.provider_name , 
            account_label = data.account_label , 
            wallet_address = data.wallet_address , 
            network = data.network ,
            external_account_id = data.external_account_id , 
            sync_status = data.sync_status ,
        )

        try :
            await self.db.add(source)
            await self.db.commit()
            await self.db.refresh(source)
            return source 
        except IntegrityError:
            await self.db.rollback()
            raise PortfolioSourceConflict()
        
    # get portfolio source , portolio_id as paramete , all soruces

    async def getting_portfolio_sources(self, portfolio_id: int) -> list[PortfolioSources]:

        result = await self.db.execute(select(PortfolioSources).where(PortfolioSources.portfolio_id == portfolio_id))
        return result.scalars().all()
    
    #  get portfolio source , portfolio_id and source_id , specific one 

    async def getting_portfolio_source(self , portfolio_id : int , source_id : int ) -> PortfolioSources :

        result = await self.db.execute(select(PortfolioSources).where(PortfolioSources.portfolio_id ==portfolio_id , 
                PortfolioSources.source_id ==  source_id ))
        portfolio_source = result.scalars().first()

        if portfolio_source is None :
            raise PortfolioSourceNotFound()
        
        return portfolio_source
    

    # patch , portfoli source update , portfolio_id and source_id
    async def update_portfolio_source(self , portfolio_id : int , soruce_id : int , data :  PortfolioSourceUpdate) -> PortfolioSources :

        portfolio_source = self.getting_portfolio_source(portfolio_id  , soruce_id)
        
        update_source = data.model_dump(exclude_unset=True)        
    
        for field , value in update_source.items():
            setattr(portfolio_source, field , value)

        try : 
            await self.db.commit()
            await self.db.refresh(portfolio_source)
            return portfolio_source
        except IntegrityError :
            await self.db.rollback()
            raise PortfolioSourceConflict()
        

    # delete , portfolio source detele , portfolio_id and source_id
    
    async def archive_portfolio_source( self , portfolio_id : int , source_id:int ) -> None : 

        result = await self.db.execute(select(PortfolioSources).where(PortfolioSources.portfolio_id ==portfolio_id ,
                PortfolioSources.source_id == source_id))
        portfolio_source_delete = result.scalars().first()
        

        if not portfolio_source_delete:
            raise PortfolioSourceNotFound()

        try : 
            await self.db.delete(portfolio_source_delete)
            await self.db.commit()
        except IntegrityError :
            await self.db.rollback()
            raise  NoContent()



class AssetsService :
    
    async def __init__(self , db : AsyncSession):
        self.db = db

    # asset listing  - by exact ID 
    
    async def list_assets(self , asset_id : int  ):
        result = await self.db.execute(select(Assets).where(Assets.asset_id == asset_id))
        asset = result.scalars().first()


        if not asset :
            raise AssetNotFound()
        
        return asset

    # asset listing by serch/filter  , name  ,type  etc 
    #* searching and fitering 

    async def get_assets(self , search_term: str = None , filter_type : str = None , sort_by : str = "name" , sort_order : str = "asc" , offset : int = 0 ,limit : int = 10 ):
        
        # define base query 

        asset  = await self.db.execute(select(Assets))

        if search_term is not None  and search_term.strip() != "" :

            match_pattern = f"%{search_term}%"
            asset = asset.filter(
                (Assets.name.ilike(match_pattern)) | 
                (Assets.asset_type.ilike(match_pattern)) |
                (Assets.symbol.ilike(match_pattern))
            )
        # for a specific type
        if filter_type is not None :
            asset= asset.filter(Assets.asset_type == filter_type)

        sort_mapping = {
            "name" : Assets.name ,
            "asset_type" : Assets.asset_type,
            "symbol" : Assets.symbol
        }

        target_column = sort_mapping.get(sort_by , Assets.name)

        if sort_order == "desc":
            asset = asset.order_by(target_column.desc())
        else :
            asset = asset.order_by(target_column.asc())

        asset = asset.offset(offset).limit(limit)

        return asset.all()
    
    