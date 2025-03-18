import tripdata_cleaning as tripdata
import matplotlib.pyplot as plt
import seaborn as sns
import folium as f
from folium.plugins import HeatMap
from sklearn.cluster import KMeans as KM
import pandas as pd
import numpy as np
from tabulate import tabulate as t


from folium.plugins import HeatMap as ht

#check for the outliners

sns.histplot(tripdata.geo_df['Geodesic_trip_Distance'],kde=True)
plt.title('Trip distance')
plt.show()

sns.histplot(tripdata.df['trip_time_in_minutes'],kde=True)
plt.title('Trip time')
plt.show()

#set base map for pickup points
pickup_basemap=f.Map(location=[40.82441,-73.9518],zoom_start=10)
f.Marker([40.82441,-73.9518],radius=0.5,color='blue', fill=True,popup=f.Popup("pickup_points")).add_to(pickup_basemap)
pickup_basemap.save("pickupmap.html")

for i,row in tripdata.geo_df.iterrows():
    f.Marker( location=[row["pickup_geometry_point"].y,row["pickup_geometry_point"].x],popup=f.Popup("pickup_points"),color='blue', fill=True).add_to(pickup_basemap)
pickup_basemap.save("pickupmap.html")


#set base map for dropoff points
drop_off_basemap=f.Map(location=[40.82441,-73.9518],zoom_start=10)
f.Marker([40.82441,-73.9518],icon=f.Icon(color="red",icon="home"), fill=True,popup=f.Popup("drop_off_points")).add_to(drop_off_basemap)
drop_off_basemap.save("dropoffmap.html")

for i,row in tripdata.geo_df.iterrows():
    f.Marker( location=[row["dropoff_latitude"],row["dropoff_longitude"]],icon=f.Icon(color="red",icon="home"),popup=f.Popup("drop_off_points"), fill=True).add_to(drop_off_basemap)
drop_off_basemap.save("dropoffmap.html")


#set base map for pickup and dropoff points

trip_distance=f.Map(location=[40.82441,-73.9518],zoom_start=10)

for i,row in tripdata.geo_df.iterrows():

    f.Marker( location=[row["dropoff_latitude"],row["dropoff_longitude"]],icon=f.Icon(color="red",icon="home"),popup=f.Popup("drop_off_points"), fill=True).add_to(trip_distance)


    f.Marker( location=[row["pickup_geometry_point"].y,row["pickup_geometry_point"].x],icon=f.Icon(color="blue",icon="home"),popup=f.Popup("drop_off_points"), fill=True).add_to(trip_distance)
            

trip_distance.save("trip_map.html")


pickups=tripdata.df[['pickup_latitude','pickup_longitude']]
pickups.dropna(inplace=True)
print(pickups.head())
pickup_heatmap=f.Map(location=[40.75011,-73.9939],zoom_start=12)
HeatMap(pickups,radius=15,min_opacity=0.2,blur=20).add_to(f.FeatureGroup(name='Hmap').add_to(pickup_heatmap))
f.LayerControl().add_to(pickup_heatmap)
pickup_heatmap.save("heatmap_for_SF.html")

#Apply K means Clustering to find nearby trips based on pickuplocations or starting point

pickup_locations= tripdata.geo_df[['pickup_latitude','pickup_longitude']]
KM=KM(n_clusters=4, random_state=0)
KM.fit(pickup_locations)
tripdata.geo_df['KMeans_cluster']=KM.labels_

print(tripdata.geo_df.head())
np.set_printoptions(suppress=True)
print(KM.cluster_centers_)
print(KM.labels_)
print(tripdata.geo_df[['pickup_latitude','pickup_longitude','KMeans_cluster']])

#use previous base map for pickup points

for i,row in tripdata.geo_df.iterrows():
    f.Marker( location=[row["pickup_geometry_point"].y,row["pickup_geometry_point"].x],popup=f"cluster:{row['KMeans_cluster']}",
            icon=f.Icon(color='blue'
                        if row['KMeans_cluster']==0
                        else 'yellow'
                        if row['KMeans_cluster']==1
                        else'green'
                        if row['KMeans_cluster']==2
                        else'red'),
                        fill=True).add_to(pickup_basemap)
pickup_basemap.save("tripcluster.html")


# Calculate average trip distance for each cluster

avg_trip_distance=tripdata.geo_df.groupby('KMeans_cluster')['Geodesic_trip_Distance'].mean().reset_index(name='Average Trip Distance')
print(avg_trip_distance.to_string(index=False))

#output-

# KMeans_cluster  Average Trip Distance
#               0               4.043758
#               1               0.000000
#               2               2.888295
#               3              20.806809


## Find the frequency of trips by an hour

tripdata.geo_df['hour']=tripdata.geo_df['tpep_pickup_datetime'].dt.hour
print(tripdata.geo_df['tpep_pickup_datetime'],tripdata.geo_df['hour'])
tripdata.geo_df['day']=tripdata.geo_df['tpep_pickup_datetime'].dt.date

trip_frequencies=tripdata.geo_df.groupby('hour').size() 
print("frequency of trips by an hour:\n")
print(trip_frequencies)

# output-hour---->
# frequency of trips by an hour:

# hour
# 0     21
# 13    12
# 19    24
# 20    14

## calculate average tip amount paid for each cluster
avg_tip_by_cluster=tripdata.geo_df.groupby('KMeans_cluster')['tip_amount'].mean().reset_index(name='Average Tip')
print("Average tip paid: \n")
print(avg_tip_by_cluster.to_string(index=False))

#output--->
# Average tip paid:

#  KMeans_cluster  Average Tip
#               0     2.149375
#               1     0.783333
#               2     1.586400
#               3     3.000000



#Find frequent Start and End points for each KMeans Cluster
frequent_start_point=tripdata.geo_df.groupby('KMeans_cluster')[['pickup_latitude','pickup_longitude']].mean()

frequent_end_point=tripdata.geo_df.groupby('KMeans_cluster')[['dropoff_latitude','dropoff_longitude']].mean()

print(frequent_start_point,frequent_end_point)

#output---->
#                 pickup_latitude  pickup_longitude
# KMeans_cluster
# 0                     40.782260        -73.932736
# 1                      0.000000          0.000000
# 2                     40.739312        -73.990032
# 3                     40.644241        -73.784809
#                 dropoff_latitude  dropoff_longitude
# KMeans_cluster
# 0                      40.775434         -73.963724
# 1                       0.000000           0.000000
# 2                      40.738378         -73.981896
# 3                      40.751444         -73.986599


#Find frequent routes for each cluster
routes=tripdata.geo_df.groupby(['KMeans_cluster','pickup_latitude','pickup_longitude','dropoff_latitude','dropoff_longitude']).size().reset_index(name='count')
routes.reset_index(drop=True,inplace=True)
print(routes)
frequent_routes=routes.loc[routes.groupby('KMeans_cluster')['count'].idxmax()]
frequent_routes.reset_index(drop=True,inplace=True)
print("Frequent Routes in each cluster: \n")
print(frequent_routes.to_string(index=False))
print(t(frequent_routes))

#output---->
# KMeans_cluster  pickup_latitude  pickup_longitude  dropoff_latitude  dropoff_longitude  count
#               0        40.762852        -73.933945         40.770947         -73.917023      1
#               1         0.000000          0.000000          0.000000           0.000000      3
#               2        40.684872        -73.977943         40.725510         -73.996490      1
#               3        40.644127        -73.786575         40.743530         -73.985603      1


















































