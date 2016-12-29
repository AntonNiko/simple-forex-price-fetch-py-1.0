import time
import json
import urllib.request

class Time():
    startTime = None
    
    def __init__(self):
        self.startTime = time.asctime()
	
    def waitNextFetch(self,interval):
        ## Fetch start second
        secStart = int(time.asctime()[17:19])

        ## Calculate the seconds in which the interval can be applied
        intervalSecs = []
        index = 0
        while True:
            intervalSecs.append(interval*index)
            index+=1
            if intervalSecs[-1]>59:
                del(intervalSecs[-1])
                break
   
        ## Wait until the next interval is reached and which is not the current second
        while True:
            secCur = int(time.asctime()[17:19])          
            if secCur in intervalSecs and secCur!=secStart:
                return True
            time.sleep(0.05)
            	    		
class Rates():
    allRates = {"AUD/USD":[],
                "EUR/CHF":[],
                "EUR/GBP":[],
                "EUR/JPY":[],
                "EUR/USD":[],
                "GBP/JPY":[],
                "GBP/USD":[],
                "USD/CAD":[],
                "USD/CHF":[],
                "USD/JPY":[]
                }
    
    @staticmethod
    def parseTable(t):
        rates = {}
        ## Remove <table> tags
        t = t.replace("<table>","")
        t = t.replace("</table>","")

        ## Seperate each row into its own list and remove HTML tags & Special Characters
        t = t.split("</tr><tr>")
        for i in range(len(t)):
            t[i] = t[i].split("</td><td>")
            for j in range(len(t[i])):
                t[i][j] = t[i][j].replace("<td>","")
                t[i][j] = t[i][j].replace("</td>","")
                t[i][j] = t[i][j].replace("<tr>","")
                t[i][j] = t[i][j].replace("</tr>","")
                t[i][j] = t[i][j].replace("\r\n","")
		  
        ## Set each list row to a dictionary for easy access
        for i in range(len(t)):
            symbol = t[i][0]
            bid = t[i][2]+t[i][3]
            ask = t[i][4]+t[i][5]
            low = t[i][6]
            high = t[i][7]
            timestamp = time.asctime()
            rates[symbol] = {"bid":bid,"ask":ask,"low":low,"high":high,"timestamp":timestamp}
        return rates

    def fetchData():
        try:
            response = urllib.request.urlopen("http://webrates.truefx.com/rates/connect.html?f=html")
            data = response.read().decode()
            rates = Rates.parseTable(data)
        except:
            print("Unable to complete HTTP Request.")
            return None
        return rates		
	
    def fetchRates(self):
        rates = Rates.fetchData()
        # Return if data is unable to be fetched
        if rates is None:
            return
        
        for symbol in rates.keys():
            self.allRates[symbol].append([rates[symbol]["bid"],rates[symbol]["timestamp"]])

    def writeToFile(self):
        ## Fetch JSON and convert to data that can be manipulated
        try:
            with open("rates.json","r") as f:
                dataRaw = f.read()
                data = json.loads(dataRaw)
        except FileNotFoundError:
            data = {"AUD/USD":[],"EUR/CHF":[],"EUR/GBP":[],"EUR/JPY":[],
                    "EUR/USD":[],"GBP/JPY":[],"GBP/USD":[],"USD/CAD":[],
                    "USD/CHF":[],"USD/JPY":[]}

        ## Place the last index of each currency in the data
        try:
            for symbol in self.allRates.keys():
                data[symbol].append(self.allRates[symbol][-1])
        except IndexError:
            pass

        ## Write the data to JSON File and Close
        with open("rates.json","w") as f:
            dataJSON = json.dumps(data,indent=2,sort_keys=True)
            f.write(dataJSON)

def fetchValidInterval():
    while True:
        try:
            interval = int(input("Fetch data interval in seconds: "))
            ## If the interval doesn't fit into 60 seconds, return error
            if interval in [x for x in range(1,60) if 60%x!=0]:
                print("The Interval cannot be divided equally into 60 seconds. Please Input an appropriate time interval")
                continue
        except ValueError:
            print("Invalid interval, please enter an integer")
            continue
        else:
            if interval<1:
                print("Interval must be greater than 0. Try again")
                continue
            break
    return interval
		
def main():
    ## Initialize Time and Rates Class instances
    clock = Time()
    currency = Rates()
    interval = fetchValidInterval()

    ## Start recording tick prices of 10 pairs & store in JSON file
    while True:
        clock.waitNextFetch(interval)
        currency.fetchRates()
        currency.writeToFile()
        print("Data Fetched at {} second interval".format(interval))


if __name__ == "__main__":
    main()
