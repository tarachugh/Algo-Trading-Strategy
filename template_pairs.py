from helpers import *

import numpy as np
import pandas as pd
import math


# Assign an integer key to each parameter set you want to trade.
PARAMS = {
    1: {'lookback': 30},
    2: {'lookback': 60},
    3: {'lookback': 90},
    4: {'lookback': 150},
    5: {'lookback': 180},


}


# List weight per parameter-set key per market.
# Individual weights must be positive.
# Sum of all weights must be 1.
MARKET_WEIGHTS = {
    ('ES', 'NQ'): {1: 0.10, 2: 0.10, 3: 0.30, 4: .25, 5: .25},
    ('ES', 'GC'):  {1: 0.25, 2: 0.25, 3: 0.20, 4: 0.15, 5: 0.15}
}
check_valid_weights(MARKET_WEIGHTS, PARAMS, True)


def trade_logic(market1, market2, params):

    df = load_data(market1, market2)
    df["spread"] = df['Close '+ market1] - df['Close '+ market2]
    df["historical_std"] = df['spread'].rolling(params["lookback"]).std(ddof=0)
    df["historical_mean"] = df['spread'].rolling(params["lookback"]).mean()
    df["Position_"+ market1] = 0
    df["Position_" + market2]= 0
    # conditions for shorting/longing each future:
        # df["spread"] > (df["historical_mean"] + (2* df["historical_std"])) --> short mkt1, long mkt2
        # df["spread"] < (df["historical_mean"] - (2* df["historical_std"])) --> long mkt1, short mkt2

    df["Position_"+ market1] = np.where(df["spread"] > (df["historical_mean"] + (2* df["historical_std"])), 
                                        -1, df["Position_"+ market1]) 
    df["Position_"+ market1] = np.where(df["spread"] < (df["historical_mean"] - (2* df["historical_std"])), 
                                         1, df["Position_"+ market1])
        
    df["Position_"+ market2] = np.where(df["spread"] > (df["historical_mean"] + (2* df["historical_std"])), 
                                        1, df["Position_"+ market2]) 
    df["Position_"+ market2] = np.where(df["spread"] < (df["historical_mean"] - (2* df["historical_std"])), 
                                         -1, df["Position_" + market2])
    # I am currently doing more research into whether or not I should implement stop loss here  
        
   

    df['RawPnL_' + market1] = df['Position_'+market1] * (df['Close '+market1].shift(-1) - df['Close '+market1])
    df['RawPnL_' + market2] = df['Position_'+market2] * (df['Close '+market2].shift(-1) - df['Close '+market2])
    df["Raw PnL"] = df['RawPnL_' + market1] + df['RawPnL_' + market2]
    
    df['Returns_'+ market1] = df['RawPnL_'+ market1] / df['Spliced '+market1]
    df['Returns_'+ market2] = df['RawPnL_'+ market2] / df['Spliced '+market2]
    df["Returns"] = df['Returns_'+ market1]  + df['Returns_'+ market2]

    


    # df must include "Spliced" and daily "Raw PnL" columns
    # lookback parameter in sharpe() is optional
    return df, sharpe(df, pairs=True, lookback=params['lookback'])


if __name__ == '__main__':

    pnl, sharpe = trade_logic(
        market1 = 'ES',                                ##### EXAMPLE #####
        market2 = 'NQ',                                ##### EXAMPLE #####
        params = {'lookback': 252, 'thresh': 0.5}      ##### EXAMPLE #####
    )
    print(f'\nSharpe: {sharpe}\n')
    print(pnl)
    
