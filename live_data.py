
import wget
import os
from datetime import datetime

# datetime object containing current date and time
now = datetime.now()
# dd/mm/YY H:M:S


print("::Running data update ... ",now.strftime("%d/%m/%Y %H:%M:%S"))

files = ["./dataset/time_series_19-covid-Confirmed.csv",
         "./dataset/time_series_19-covid-Deaths.csv",
         "./dataset/time_series_19-covid-Recovered.csv"]
try:
    for x in files:
        os.remove(x)
except:
    print("::File (", x, ") not present")

urls= ["https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv",
       "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv",
       "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv"]

output_directory="./dataset"


for u in urls:
    file = wget.download(u, out=output_directory)
