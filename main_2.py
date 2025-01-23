import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx  # For adding a basemap
from shapely.geometry import box
from mpl_toolkits.axes_grid1 import make_axes_locatable
from nwm_utils import get_conus_bucket_url, load_dataset, reproject_coordinates, get_fid, get_aggregation_code
from shapely.geometry import Polygon

def get_data():

    # Start date in Year-Month-Day format, the earliest start date can be '1979-02-01'
    start_datetime = '1990-01-01'

    # End date in Year-Month-Day format, the latest end date can be '2023-01-31'
    end_datetime = '2000-12-31'

    # Shapefile path 
    shapefile_path = "./GSLSubbasins/GSLSubbasins.shp"    

    # User-defined NWM output dataset; see above for a list of valid dataset names.
    #nwm_out_ds='Land Surface Model Output'
    nwm_out_ds = 'Streamflow output at all channel reaches/cells'

    # User-defined variable name - this variable is part of the National Water Model (NWM) output datasets
    # For a full list of NWM output variables, refer to the following website: https://ral.ucar.edu/sites/default/files/public/WRFHydroV5_OutputVariableMatrix_V5.pdf
    #variable_name = 'ACCET'
    variable_name = 'streamflow'

    # User-defined aggregation interval - valid values are 'hour', 'day', 'month', 'year'
    agg_interval='hour'

    # Set dictionary to map output name onto associated code used in the AWS bucket storage
    nwm_outputs = {
        'Land Surface Model Output': 'ldasout', 
        'Terrain Routing Output': 'rtout', 
        'Land Surface Diagnostic Output': 'lsmout', 
        'Streamflow output at all channel reaches/cells': 'chrtout'
    }

    # Get the name of the NWM output dataset from the dictionary (nwm_outputs)
    variable_code = nwm_outputs[nwm_out_ds]

    # Get the variable code for the aggregation interval
    agg_code = get_aggregation_code(agg_interval)

    # Get the S3 bucket URL for the data path
    url = get_conus_bucket_url(variable_code)

    # Load the dataset
    ds = load_dataset(url)
    print(ds)

    # Read the shapefile using GeoPandas
    gdf = gpd.read_file(shapefile_path)

    # Get the total bounds of the shapefile
    bounds = gdf.total_bounds

    # Create a bounding box as a Polygon
    bbox = Polygon([(bounds[0], bounds[1]), (bounds[0], bounds[3]), (bounds[2], bounds[3]), (bounds[2], bounds[1]), (bounds[0], bounds[1])])

    # Convert the bounding box into a GeoDataFrame
    bbox_gdf = gpd.GeoDataFrame([1], geometry=[bbox], crs=gdf.crs)  # Ensure it has the same CRS as the gdf

    # Create a layout for the plot
    fig, ax = plt.subplots(figsize=(12, 8))

    # Display the shapefile
    ax = gdf.plot( ax=ax, color='none', edgecolor='black', linewidth=2)

    # Plot the bounding box on the same plot (using the ax object from the previous plot)
    bbox_gdf.boundary.plot(ax=ax, color="red", linewidth=2)

    # Add a topographic basemap using contextily 
    ctx.add_basemap(ax, source=ctx.providers.Esri.WorldImagery, crs=gdf.crs.to_string(), alpha=0.8)

    # Add title
    ax.set_title("Great Salt Lake Basin and Bounding Box", fontsize=12)

    # Add grid lines
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Customize x and y axis labels
    ax.set_xlabel("Longitude", fontsize=12)
    ax.set_ylabel("Latitude", fontsize=12)

    # Reproject coordinates of the bounding box to match the dataset
    x_min, y_min = reproject_coordinates(ds, bounds[0], bounds[1], gdf.crs)
    x_max, y_max = reproject_coordinates(ds, bounds[2], bounds[3], gdf.crs)

    # Subset the data for the specified period and location
    ds_subset = ds[variable_name].sel(y=slice(y_min, y_max), x=slice(x_min, x_max)).loc[dict(time=slice(start_datetime,end_datetime))]
    ds_subset_df = ds_subset.mean(['x', 'y']).to_dataframe()
    print(ds_subset_df)

    # Get the attributes for the label and title
    units = ds_subset.attrs.get('units', 'Unknown Units')
    long_name = ds_subset.attrs.get('long_name', 'Unknown Variable')

    # Plot the user-defined variable
    plt.figure(figsize=(15, 6))
    plt.plot(ds_subset_df.index, ds_subset_df[ds_subset.name], label=f'{long_name}')

    # Adding additional plot details
    plt.title(f'{long_name} Time Series')
    plt.xlabel('Time')
    plt.ylabel(f'{long_name} ({units})')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Display the plot
    plt.show()

    # Specify the file path where you want to save the CSV file
    file_path = f"{variable_name}_over_area.csv"

    # Save the DataFrame to a CSV file
    ds_subset_df.to_csv(file_path, index=True)  


if __name__ == "__main__":
    print("Hello, World!")
    get_data()
