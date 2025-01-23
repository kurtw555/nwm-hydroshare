import xarray as xr
import fsspec
import pyproj
import geopandas as gpd

def get_conus_bucket_url(variable_code):
    """
    This function returns the S3 bucket url path for the CONSUS retrospective  data (in zarr format) for a given variable code.
    
    Parameters:
    variable_code (str): The code of the variable.

    Returns:
    str: S3 bucket url path for retrospective  data.
    """
    conus_bucket_url = f's3://noaa-nwm-retrospective-3-0-pds/CONUS/zarr/{variable_code}.zarr'
    return conus_bucket_url

def load_dataset(conus_bucket_url):
    """
    This function loads the dataset from the given S3 bucket url path.
    
    Parameters:
    conus_bucket_url (str): The URL of the dataset to load.

    Returns:
    xr.Dataset: The loaded dataset as a xarray dataset
    """
    ds = xr.open_zarr(
        fsspec.get_mapper(
            conus_bucket_url,
            anon=True
        ),
        consolidated=True
    )
    return ds

def reproject_coordinates(ds, lon, lat, input_crs='EPSG:4326'):
    """
    This function reprojects the given lon and lat coordinates to the dataset's CRS.
    
    Parameters:
    ds (xr.Dataset): The dataset containing the CRS information.
    lon (float): The longitude to reproject.
    lat (float): The latitude to reproject.
    input_crs (str): The CRS of the input coordinates.

    Returns:
    tuple: The reprojected coordinates (x, y).
    """
    output_crs = pyproj.CRS(ds.crs.esri_pe_string)  # CRS of AORC dataset (lcc)
    transformer = pyproj.Transformer.from_crs(input_crs, output_crs, always_xy=True)
    x, y = transformer.transform(lon, lat)
    return x, y

def get_fid(usgs_gageid):
    """
    Get the feature id for a given USGS gage id.
    
    Paramters:
    usgs_gageid (str): USGS gage ID
    
    Returns:
    str: Feature id
    """
    # Read the linked sites GeoPackage
    linked_sites = gpd.read_file("./linked_sites.gpkg")
    
    # Retrieve the COMID for the given USGS gage ID
    fid_value = linked_sites.loc[linked_sites['site_id'] == usgs_gageid, 'COMID'].iloc[0]
    
    return fid_value

def get_aggregation_code(aggr_name):
    """
    Gets a aggregation code for a given aggregation name.

    Parameters:
    aggr_name (str): Name of the aggregation
    
    Returns:
    str: A code for aggregation
    """
    agg_options = {
        'hour':'h',
        'day':'d',
        'month':'ME',
        'year':'YE'
    }
    
    if aggr_name not in agg_options:
        raise Exception(f"{aggr_name} is not a valid aggregation name")
    
    return agg_options[aggr_name]