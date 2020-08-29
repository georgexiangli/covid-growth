# Analyzing COVID-19 Growth Across Countries

## Study Description
This study uses a modified [Ten Hundred Plot](https://www.youtube.com/watch?v=NP3ZdQwrL_Q) for visualizing growth of COVID-19 deaths

* Original plot developed by [Dr. Jerry Zhu](http://pages.cs.wisc.edu/~jerryzhu/) at the University of Wisconsin - Madison

* Data collected from [COVID-19 data repository](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series) from the Center for Systems Science and Engineering at Johns Hopkins University
    * This is a time series data set that stores the number of COVID deaths each day for each country from January 22, 2020 to present
    * Extract at the time of this study had data up to July 24, 2020

## Program Files
* clustering.py - functions for processing data and performing hierarchical and k-means clustering
* COVID Growth.ipynb - Jupyter notebook to visualize results
* time_series_covid19_deaths_US.csv - data file for deaths in the United States
* time_series_covid19_deaths_global.csv - data file for deaths in the rest of the world