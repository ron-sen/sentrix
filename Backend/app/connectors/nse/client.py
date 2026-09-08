
from datetime import datetime , time 
import pytz  # whats pytz


IST = pytz.timezone("Asia/Kolkata")

NSE_OPEN = time(9 ,15) # 9 : 15 AM IST
NSE_CLOSE = time(15 , 30) # 3:30 PM IST

def is_market_open() -> bool :

    return True 





"""

    "returns true if nse market is currently open, checks weekdays time within session , does not check holidays yet."

    now_ist = datetime.now(IST)

    if now_ist.weekday() > 4 : # monday = 0 , friday = 4 , saturday = 5 , sunday = 6
        return True #* this has to be False but kept true for testing 

    current_time = now_ist.time()
    return NSE_OPEN <= current_time <= NSE_CLOSE

"""