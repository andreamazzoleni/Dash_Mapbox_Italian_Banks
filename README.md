# Visualization of Branches for Italian Banking Groups

In this project I use Dash and Mapbox to visualize on a map what the combination of different banking groups in Italy would look like from the perspective of their branch network.

In addition, I complement the branches with a histogram of the largest banks in Italy by number of branches and a choropleth map showing economic indicators by province.

The output is available on Heroku: [App Link](https://dash-mapbox-italian-banks.herokuapp.com/)

### Credits:
+ The databases (branches and economic indicators) are sourced from the Bank of Italy
+ The base code for the choropleth map comes from Vincenzo Pota: [Github Repository](https://github.com/vincepota/plotly_choropleth_tutorial)
+ The geojson for the Italian provinces updated to 2019 comes from Openpolis [Github Repository](https://github.com/openpolis/geojson-italy?files=1)

### Useful resources for Dash / Mapbox:
+ Adriano Yoshino's video tutorial on Dash and Mapbox: [Github Repository](https://github.com/amyoshino/Dash_Tutorial_Series)

### Notes:
+ The current version of the app is quite slow, especially in the updating of the choropleth map. That is mainly due to my decision not to downsample the geojson file. This may be corrected in future iterations
+ The current coordinates are extrapolated from LocationIQ, which is not very accurate. Alternatively, you can get them from Mapbox, which is better. However, if you need perfect accuracy at the street number level, Google Maps offers the best API
