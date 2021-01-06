import numpy as np
import time
import pandas as pd
import requests
import json
import functools
import operator

# requests urls
url_cities = 'https://balneabilidade.ima.sc.gov.br/municipio/getMunicipios'
url_places = 'https://balneabilidade.ima.sc.gov.br/local/getloc_detailsByMunicipio'
url_years = 'https://balneabilidade.ima.sc.gov.br/registro/anosAnalisados'
url_data = 'https://balneabilidade.ima.sc.gov.br/relatorio/historico'

url_list =[url_cities, url_places, url_years, url_data]

# extract the list of years -> used to do one request per year
years = json.loads(requests.get(url_years).text)
years = [i['ANO'] for i in years]

# makes one request per year (using url_data) 
# all the monitoring points ('localID' : 0) in Florianopólis city ('municipioID' : 2)
print('Request Loop Started')
ti = time.time()
list_req = [requests.post(url_data,
                          data={
                              "municipioID": 2,
                              "localID": 0,
                              "ano": i,
                              "redirect": True
                          }) for i in years]
tf = time.time()
print([i.status_code == 200 for i in list_req])
print()
print('Request Loop Finished in',tf-ti, 'seconds')

# creates empty lists to store the dataframes 
# 'places' -> details of locations of the monitorint points / 'data' -> data of interest
places = []
data = []


print()
print('For Loop Started')
ti2 = time.time()

# iterates over the results returned for each year
for i in list_req: 

    # reads the html and puts the tables in dataframes
    rawdata = pd.read_html(i.text)

    # the first dataframe for each year has no use
    rawdata.pop(0)

    # the dataframes alternate between location details and monitoring data
    # subsets the result for dataframes with location details 
    infodf = rawdata[0:(len(rawdata)+1):2]

    # subsets the result for dataframes with the monitoring data
    listdf = rawdata[1:(len(rawdata)+1):2]

    # extracts and wrangle the details of the location into the correct dataframe format
    infodf_new = []
    for i, j in zip (infodf, listdf):
        # for the info df, attain the point number:
        j['ponto'] = i.iloc[1, 0].lower().strip('ponto de coleta: ponto ')
        
        # transform every info df column-wise
        infodf_added = pd.DataFrame(
                    {'municipio': i.iloc[0,0].lower().replace('município: ', ''),
                    'balneario': i.iloc[0,1].lower().replace('balneário: ', ''),
                    'ponto': i.iloc[1,0].lower().replace('ponto de coleta: ponto ', ''),
                    'localizacao': i.iloc[1,1].lower().replace('localização: ', '')}, index=[0]
                )
        # create appended list of df
        infodf_new.append(infodf_added)

    # creates one dataframe with the location details of all points monitored in a year
    loc_details = pd.concat(infodf_new)
    loc_details.reset_index(drop=True, inplace=True)

    # crates one dataframe with the data from all the points monitored in a year 
    df = pd.concat(listdf)
    df.reset_index(drop=True, inplace=True)

    # append to the corresponding list of dataframes
    places.append(loc_details)
    data.append(df)
tf2 = time.time()
print()
print('For Loop Finished in', tf2-ti2, 'seconds')

# concats the data frames for each year into a single df (location details)
spots = pd.concat(places).reset_index(drop=True)
spots = spots.drop_duplicates(subset='ponto', keep='first').reset_index(drop=True)

# concats the data frames for each year into a single df (monitoring data)
df = pd.concat(data).reset_index(drop=True)

# there are a lot of missing values in the 'hour' column
# fill the na values with a "reasonable" hour, as the samples are taken in the morning
df['Hora'].fillna('09:30:00', inplace=True)

# replaces a cell where hora is wrong ('92:07:00')
df.loc[df['Hora'] == '92:07:00', ['Hora']] = '09:30:00'

# gets the date and hour columns and defines a datetime column
df['dateTime'] = pd.to_datetime(df.Data + ' ' + df.Hora)

# drops the old date and hour columns
df.drop(columns=['Data', 'Hora'], inplace=True)

# the columns with air and wates temperatures contain symbols that need to be removed
# removes the symbols and tranforms the columns into type float
def transform_colT(column):
    df[column] = df[column].apply(lambda x: x.replace(' Cº', ''))
    df[column] = df[column].apply(lambda x: x.replace('Cº', ''))
    df[column] = df[column].apply(lambda x: np.nan if isinstance(x, str) and (x.isspace() or not x) else x)
    df[column] = df[column].astype('float')
    return df[column]

df['Agua (Cº)'] = transform_colT('Agua (Cº)')
df['Ar (Cº)'] = transform_colT('Ar (Cº)')

# converts the rest of the columns to the right types
df['ponto'] = df['ponto'].astype('int')
df['Condição'] = df['Condição'].astype('category')
df['Vento'] = df['Vento'].astype('category')
df['Maré'] = df['Maré'].astype('category')
df['Chuva'] = df['Chuva'].astype('category')

# Reorder columns
cols = ['dateTime', 'ponto', 'Vento', 'Maré', 'Chuva', 'Agua (Cº)', 'Ar (Cº)', 'E.Coli NMP*/100ml', 'Condição']
df = df[cols]

# rename columns to english
df.rename(columns={'ponto': 'point', 'Vento': 'wind', 'Maré': 'tide', 'Chuva': 'rain', 
                   'Agua (Cº)': 'water_temp', 'Ar (Cº)': 'air_temp', 'E.Coli NMP*/100ml': 'e_coli', 'Condição': 'condition'}, inplace=True)

# some features of each point of monitoring were gathered manually
# this loads this features into a df
features_points = pd.read_excel('features_points.xlsx')

# adds the corresponding features to each point of monitoring
df = df.merge(features_points, left_on='point', right_on='point')

df.to_csv('df_english.csv', sep=';')