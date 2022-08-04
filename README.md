# gsc-exporter
A script to export more keyword data from Google Search Console than possible through the webinterface or using the API as intended.

When analysing keyword data on the Google Search Console (GSC) on the webinterface we are limited to the first 1000 results of our filter settings.
This limit is increased to 5000 results when using the API however even that may not suffice to analyse website with a broad spectrum of relevant keywords.

This script solves that problem by iterating relevant user provided keywords with the GSC API combining multiple API answers. 
After eliminating duplicates the script can output the collected data to a .csv or a database.


**TO ADD KEYWORDS CREATE A FILE CALLED query.csv IN THE SAME DICTIONARY AND PUT ONE KEYWORD PER ROW**




gsc-exporter-csv exports the .csv to the working directionary
gsc-exporter-db needs to be connected to a mysql-db during setup
