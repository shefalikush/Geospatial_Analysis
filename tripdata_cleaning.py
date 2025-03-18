import pandas as pd
from geopy.distance import geodesic, distance
import geopandas as gpd
from shapely.geometry import Point

df=pd.read_csv('tripdata-small.csv',header=0)
print(df.head())
print(df.columns)
print(df.info())
df.isnull().sum()

df.fillna(0,inplace=True) # optional as no null values available
df.columns=df.columns.str.strip()

print(df['tpep_pickup_datetime'].head())
#convert timestamp to datetime object
df['tpep_pickup_datetime']= pd.to_datetime(df['tpep_pickup_datetime']) #convert to datetime object
df['tpep_dropoff_datetime']=pd.to_datetime(df['tpep_dropoff_datetime'])
print(df['tpep_pickup_datetime'].head())
#new feeature trip_time_in_minutes

df['trip_time_in_minutes']=(df['tpep_dropoff_datetime']-df['tpep_pickup_datetime']).dt.total_seconds()/60
#df['trip_time_in_minutes']=df['trip_time_n'].dt.total_seconds()/60
print(df['trip_time_in_minutes'].head())


#create geometry object
point_of_pickup=[Point(ij) for ij in zip(df['pickup_longitude'],df['pickup_latitude'])]
point_of_dropoff=[Point(ij) for ij in zip(df['dropoff_longitude'],df['dropoff_latitude'])]
#create geodataframe
geo_df=gpd.GeoDataFrame(df,geometry=point_of_pickup)
geo_df=geo_df.rename(columns={'geometry':'pickup_geometry_point'})
geo_df.set_geometry('pickup_geometry_point',inplace=True)
geo_df['dropoff_geometry_point']=point_of_dropoff



geo_df.set_crs('EPSG:4326', inplace=True) #set standard coordinate system
print(geo_df)

#calculate distance using longitude and latitude
def haversine(pickup_lat,pickup_long,dropoff_lat,drop_off_long):
    return geodesic((pickup_lat,pickup_long),(dropoff_lat,drop_off_long)).kilometers

def calulate_Geodesic_Distance(r):
    return haversine(r['pickup_latitude'],r['pickup_longitude'],r['dropoff_latitude'],r['dropoff_longitude'])
#new feature Geodesic_trip_Distance'
geo_df['Geodesic_trip_Distance']=geo_df.apply(calulate_Geodesic_Distance,axis=1)

print(geo_df['Geodesic_trip_Distance'].head())
print(geo_df.info())


geo_df['correct_geo_object']=geo_df.is_valid
print(geo_df[geo_df['correct_geo_object']==False])

geo_df.to_file('trip_data_with_geometry', driver='GeoJSON') #covert to GeoJSOn format
print(geo_df.describe())
print(geo_df.info())
print()
