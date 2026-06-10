
# it handles the error related to db conflict 

from sqlalchemy.exc import IntegrityError 
from sqlalchemy.orm import Session
from app.db.connection import get_db
from fastapi import Depends
from typing import Annotated

from app.models.portfolio_auth import PortfolioInfo  ,Assets , PortfolioSources
from app.schemas.portfolio_validation import ValidatePortfolio , PortfolioResponse ,PortfolioUpdate  , AssetsInfo , AssetsResponse , PortfolioSourceValidation , PortfolioSourceResponse , PortfolioSourceUpdate , FilterParams , SortOrder , SortFields

from app.security.jwtsecure import get_current_user

from app.services.exception import PortfolioSourceConflict , PortfolioSourceNotFound,NoContent , AssetNotFound


class PortfolioServices :

    def __init__(self , db : Session):
        self.db = db

    # post / portfolio source  , portolio_id as parameter
    def creating_portfolio_info(self , portfolio_id : int , data : PortfolioSourceValidation):
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
            self.db.add(source)
            self.db.commit()
            self.db.refresh(source)
            return source 
        except IntegrityError:
            self.db.rollback()
            raise PortfolioSourceConflict()
        
    # get portfolio source , portolio_id as paramete , all soruces

    def getting_portfolio_sources(self, portfolio_id: int) -> list[PortfolioSources]:
        return (
            self.db.query(PortfolioSources)
            .filter(PortfolioSources.portfolio_id == portfolio_id).all()
    )
    #  get portfolio source , portfolio_id and source_id , specific one 

    def getting_portfolio_source(self , portfolio_id : int , source_id : int ) -> PortfolioSources :
        portfolio_source =(
            self.db.query(PortfolioSources).filter(
                PortfolioSources.portfolio_id ==portfolio_id , 
                PortfolioSources.source_id ==  source_id 
        ).first()
    
    )

        if portfolio_source is None :
            raise PortfolioSourceNotFound()
        
        return portfolio_source
    

    # patch , portfoli source update , portfolio_id and source_id
    def update_portfolio_source(self , portfolio_id : int , soruce_id : int , data :  PortfolioSourceUpdate) -> PortfolioSources :

        portfolio_source = self.getting_portfolio_source(portfolio_id  , soruce_id , current_user=None)
        
        update_source = data.model_dump(exclude_unset=True)        
    
        for field , value in update_source.items():
            setattr(portfolio_source, field , value)

        try : 
            self.db.commit()
            self.db.refresh(portfolio_source)
            return portfolio_source
        except IntegrityError :
            self.db.rollback()
            raise PortfolioSourceConflict()
        

    # delete , portfolio source detele , portfolio_id and source_id
    
    def archive_portfolio_source( self , portfolio_id : int , source_id:int ) -> None : 
        portfolio_source_delete = (
            self.db.query(PortfolioSources).filter(
                PortfolioSources.portfolio_id ==portfolio_id ,
                PortfolioSources.source_id == source_id 
            ).first()
        )

        if not portfolio_source_delete:
            raise PortfolioSourceNotFound()

        try : 
            self.db.delete(portfolio_source_delete)
            self.db.commit()
        except IntegrityError :
            self.db.rollback()
            raise  NoContent()



class AssetsService :
    
    def __init__(self , db : Session):
        self.db = db

    # asset listing  - by exact ID 
    
    def list_assets(self , asset_id : int  ):
        asset =  self.db.query(Assets).filter(
            Assets.asset_id == asset_id 
        ).first()


        if not asset :
            raise AssetNotFound()
        
        return asset

    # asset listing by serch/filter  , name  ,type  etc 
    #* searching and fitering 

    def get_assets(self , search_term: str = None , filter_type : str = None , sort_by : str = "name" , sort_order : str = "asc" , offset : int = 0 ,limit : int = 10 ):
        
        # define base query 

        asset = self.db.query(Assets)

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
    
    