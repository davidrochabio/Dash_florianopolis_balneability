# Bathing Water Quality (balneability) - City of Florianópolis-SC, Brazil

This project seeks to analyze data and gain meaningful insights about the water quality of the beaches in the city of Florianópolis-SC, Brazil.

Balneability is defined as the quality of waters for recreacional use, for instance, to bath, swim and water sports activities.

The water quality is assessed by the measument of the quantity of bacteria (in the case E. Coli) present in the time of sampling.

##### Pipeline

1 - The first dataset was taken from the state's official website: https://balneabilidade.ima.sc.gov.br/. A script (Balneability.py) was developed to perform multiple requests to the website (one for each year) and return multiple html pages with the tables. The tables were manipulated in order to organize the data into two dataframes -> one with all the variables of interest and other with location details for each point. Then, these wto dataframes were merged into a single dataframe.

This dataset includes the sampling of 87 points throughout the city since 1995 (the time period of measurements differs for each point). Generally, the samples are taken once every week in summer (november to march), and once every month in winter (april to october).

Variables: dateTime, point, wind, tide, rain, water_temp, air_temp, e_coli, condition

2 - The second dataset was created by hand, as this was the only form to gather the data of interest. For each point it was obtained the geographic coordinates and three other variables:

Variables: lat = latitude, long = longitude, location = relative location of the point in the island (north, west, east, etc.), drenage_beach = if the beach, as whole, has any rivers and rain drenages that flow into the ocean, drenage_point = if the point has rivers and rain drenages that flow into the ocean right next to it.

At the end of the pipeline, the two datasets were merged into a single dataset with all the variable and saved as 'df.csv'

### Visual EDA - Dash

After all the data of interest was gathered, a dashboard was develop in order to perform exploratory data analysis. For this, Dash and Plotly libraries were used

The dashboard contains a map of Florianópolis with all the points. Then it is possible to compare two point of monitoring in terms of their distributions and timeseries for the main variable of interest, bacteria in the water (E. Coli). It also contains tables with summary statistics per point, per year and per month.

For environment requirements, check requirements files (pip and conda).

In colaboration with Andhros Guimarães: https://github.com/Andhros

