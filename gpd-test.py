import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from shapely.geometry import Polygon
from geopandas import GeoSeries
import contextily as ctx  # For adding a basemap


if __name__ == "__main__":
    print("Hello, World!")

    # Shapefile path 
    shapefile_path = "./GSLSubbasins/GSLSubbasins.shp"

    # Load from a shapefile
    gdf = gpd.read_file(shapefile_path)

    # Get the total bounds of the shapefile
    bounds = gdf.total_bounds

    # Create a bounding box as a Polygon
    bbox = Polygon([(bounds[0], bounds[1]), (bounds[0], bounds[3]), (bounds[2], bounds[3]), (bounds[2], bounds[1]), (bounds[0], bounds[1])])

    # Convert the bounding box into a GeoDataFrame
    bbox_gdf = gpd.GeoDataFrame([1], geometry=[bbox], crs=gdf.crs)  # Ensure it has the same CRS as the gdf

    # Create a layout for the plot
    fig, ax = plt.subplots(figsize=(12, 8))

    # Or, create a GeoDataFrame from scratch
    #data = {'geometry': [Point(1, 2), Point(3, 4)]}
    #gdf = gpd.GeoDataFrame(data, crs="EPSG:4326") 

    # Display the shapefile
    ax = gdf.plot( ax=ax, color='none', edgecolor='black', linewidth=2)
    #ax = gdf.plot()

    # Add a topographic basemap using contextily 
    ctx.add_basemap(ax, source=ctx.providers.Esri.WorldImagery, crs=gdf.crs.to_string(), alpha=0.8)
    plt.savefig('file1')
    #plt.show()

    ival = 1