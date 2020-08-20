import sys
import numpy as np
import pandas as pd

def SMA(pastData,currentPrice,windowSize):
    SMAu = 0
    SMAd = 0
    temp = pastData[-windowSize:]
    for i in range(windowSize-1):
        if temp[i]<temp[i+1]:
            SMAu += temp[i+1]-temp[i]
        else:
            SMAd += temp[i]-temp[i+1]
    return SMAu/windowSize,SMAd/windowSize
# Decision of the current day by the current price, with 3 modifiable parameters
def myStrategy(pastData, currentPrice, windowSize, low, up):
    action = 0
    if(len(pastData)<5):
        action = 0
        return action
    if(len(pastData)<windowSize):
        windowSize = len(pastData)
    SMAu,SMAd = SMA(pastData, currentPrice, windowSize)
    value = SMAu/(SMAu+SMAd)
    if(np.round(value*100)>up):
        action = -1
    if(np.round(value*100)<low):
        action = 1
    return action

# Compute return rate over a given price vector, with 3 modifiable parameters
def computeReturnRate(priceVec, windowSize, low, up):
	capital=1000	# Initial available capital
	capitalOrig=capital	 # original capital
	dataCount=len(priceVec)				# day size
	suggestedAction=np.zeros((dataCount,1))	# Vec of suggested actions
	stockHolding=np.zeros((dataCount,1))  	# Vec of stock holdings
	total=np.zeros((dataCount,1))	 	# Vec of total asset
	realAction=np.zeros((dataCount,1))	# Real action, which might be different from suggested action. For instance, when the suggested action is 1 (buy) but you don't have any capital, then the real action is 0 (hold, or do nothing). 
	# Run through each day
	for ic in range(dataCount):
		currentPrice=priceVec[ic]	# current price
		suggestedAction[ic]=myStrategy(priceVec[0:ic], currentPrice, windowSize, low, up)		# Obtain the suggested action
		# get real action by suggested action
		if ic>0:
			stockHolding[ic]=stockHolding[ic-1]	# The stock holding from the previous day
		if suggestedAction[ic]==1:	# Suggested action is "buy"
			if stockHolding[ic]==0:		# "buy" only if you don't have stock holding
				stockHolding[ic]=capital/currentPrice # Buy stock using cash
				capital=0	# Cash
				realAction[ic]=1
		elif suggestedAction[ic]==-1:	# Suggested action is "sell"
			if stockHolding[ic]>0:		# "sell" only if you have stock holding
				capital=stockHolding[ic]*currentPrice # Sell stock to have cash
				stockHolding[ic]=0	# Stocking holding
				realAction[ic]=-1
		elif suggestedAction[ic]==0:	# No action
			realAction[ic]=0
		else:
			assert False
		total[ic]=capital+stockHolding[ic]*currentPrice	# Total asset, including stock holding and cash 
	returnRate=(total[-1]-capitalOrig)/capitalOrig		# Return rate of this run
	return returnRate

if __name__=='__main__':
	returnRateBest=-1.00	 # Initial best return rate
	df=pd.read_csv(sys.argv[1])	# read stock file
	adjClose=df["Adj Close"].values		# get adj close as the price vector
	windowMin=5; windowMax=40;	# Range f windowSize to explore
	lowMin=1;	lowMax = 40
	upMin = 60; upMax = 99			# Range of alpha to explore
	#betaMin=13; betaMax=18				# Range of beta to explore
	# Start exhaustive search
	windowSizeBest=0
	lowBest = 0
	upBest = 0
	for windowSize in range(windowMin, windowMax+1):		# For-loop for windowSize
		print("windowSize=%d" %(windowSize))
		for low in range(lowMin, lowMax+1):	    	# For-loop for alpha
			print("\tlow=%d" %(low))
			for up in range(upMin,upMax+1):
				print("\tup=%d" %(up))

				returnRate=computeReturnRate(adjClose, windowSize, low, up)		# Start the whole run with the given parameters
				print(" ==> returnRate=%f " %(returnRate))
				if returnRate > returnRateBest:		# Keep the best parameters
					windowSizeBest = windowSize
					lowBest = low
					upBest = up
					returnRateBest=returnRate
	print("Best settings: windowSize=%d, low=%d, up=%d ==> returnRate=%f" %(windowSizeBest,lowBest,upBest,returnRateBest))		# Print the best result
