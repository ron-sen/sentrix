

class AppError(Exception):
    status_code = 500
    detail = "Internal server error"

class PortfolioNotFound(AppError):
    status_code = 404
    detail = "portfolio not found"

class PortfolioConflict(AppError):
    status_code = 409
    detail = "Portfolio conflict"

class PortfolioSourceConflict(AppError):
    status_code = 409 
    detail = "Source conflict"
class PortfolioSourceNotFound(AppError):
    status_code = 404
    detail ="Source not found"

class NoContent(AppError):
    status_code = 204
    detail = "No content avialable"

class AssetNotFound(AppError):
    status_code = 404 , 
    detail = "Asset not found !"