
import wget
import os
from datetime import datetime

# datetime object containing current date and time
now = datetime.now()
# dd/mm/YY H:M:S


print(":: Running data update ... ",now.strftime("%d/%m/%Y %H:%M:%S"))
output_directory="./dataset"

files = ["/time_series_covid19_confirmed_global.csv",
         "/time_series_covid19_deaths_global.csv",
         "/time_series_covid19_recovered_global.csv"
         ]
         

for x in files:
    try:
        final = output_directory + x
        os.remove(output_directory + x)
        print(final)
        wget.download("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series"+x, out=output_directory)
    except:
        wget.download("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series"+x, out=output_directory)
        print("::File (", x, ") not present")


# urls= ["https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv",
#        "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv",
#        "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv"]



# for u in urls:
#     file = wget.download(u, out=output_directory)
