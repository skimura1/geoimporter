apt-get install python3-tk
pip install GDAL==$(gdal-config --version | awk -F'[.]' '{print $1"."$2}')
pip install geopandas sqlalchemy geoalchemy2 psycopg2 geoserver-rest python-dotenv tk