# FlatFinder
A small project to scrape available flats from a webpage, but mainly to try out scraping, fastAPI and SQLAlchemy.

## Web Scraper
* Simple beautiful soup scraper.

## Data storage
* Data are stored in a few MariaDB tables

## Communication
* Few API endpoints manage writing/reading data to/from the database.

## Flat evaluation
* Several dimensions can be pre-defined to check if a flat is suitable
* Location check: check if flat is in a pre-defined polygon (geojson file). Polygons can e.g. be created with [umap](https://umap.openstreetmap.de/en)

