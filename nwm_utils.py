import xarray as xr
import fsspec
from fsspec import FSMap
import zarr
import logging
import s3fs

logger = logging.getLogger("")

def get_conus_bucket_url(variable_code):
    """
    This function returns the S3 bucket url path for the CONSUS retrospective  data (in zarr format) for a given variable code.
    
    Parameters:
    variable_code (str): The code of the variable.

    Returns:
    str: S3 bucket url path for retrospective  data.
    """
    #conus_bucket_url = f's3://noaa-nwm-retrospective-3-0-pds/CONUS/zarr/{variable_code}.zarr'
    conus_bucket_url = f'noaa-nwm-retrospective-3-0-pds/CONUS/zarr/{variable_code}.zarr'
    return conus_bucket_url

def load_dataset(conus_bucket_url):
    """
    This function loads the dataset from the given S3 bucket url path.
    
    Parameters:
    conus_bucket_url (str): The URL of the dataset to load.

    Returns:
    xr.Dataset: The loaded dataset as a xarray dataset
    """
    logger.info(f"Loading dataset from {conus_bucket_url}")
    fs = fsspec.filesystem('s3', anon=True, asynchronous=True)  # Use anonymous access to S3
    store = zarr.storage.FsspecStore(fs, path=conus_bucket_url)
    ds = xr.open_zarr(store, consolidated=True)  # Load the dataset using xarray
    logger.info(f"Dataset loaded successfully from {conus_bucket_url}")
    return ds
    #ds = xr.open_zarr(
    #    fsspec.get_mapper(
    #        conus_bucket_url,
    #        anon=True
    #    ),
    #    consolidated=True
    #)
    #return ds



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

def get_data(start_date:str, end_date:str, comids:list, file_name:str):
    
    # Start date in Year-Month-Day format, the earliest start date can be '1979-02-01'    
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
    ds = load_dataset(url)
    
    # Load the dataset    
    com_ids = comids
    length = len(com_ids)
    
    ds_subset = ds[variable_name].sel(feature_id=ds.feature_id.isin(com_ids)).loc[dict(time=slice(start_date,end_date))]
    #ds_subset_df = ds_subset.mean(['x', 'y']).to_dataframe()
    # Specify the file path where you want to save the CSV file
    #file_path = f"{file_name}_{start_date}_{end_date}.csv"

    # Save the DataFrame to a CSV file
    logger.info(f"Saving data to dataframe")
    df = ds_subset.to_dataframe()
    logger.info(f"Saving data to {file_name}")
    df.to_csv(file_name, index=True)
            
    return
