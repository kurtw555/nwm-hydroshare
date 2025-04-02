import sys
import os
import logging
import logging.handlers
from logging.handlers import TimedRotatingFileHandler
import json
from datetime import datetime
from nwm_utils import get_data

LOGFILE = "nwm_retrospective.log"
logger = logging.getLogger("")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        TimedRotatingFileHandler(LOGFILE, when="midnight", interval=1),
        logging.StreamHandler(sys.stdout)
    ]
)

#National Water Model (NWM) CONUS Retrospective Dataset
# https://registry.opendata.aws/nwm-archive/
# Dataset - February 1979 through January 2023
start_data = datetime.strptime("1979-02-01", "%Y-%m-%d")  # Start of the NWM retrospective dataset
end_data = datetime.strptime("2023-01-31", "%Y-%m-%d")  # End of the NWM retrospective dataset

    
#Read parameters from a file and return the data a JSON object
def read_params(file_path: str):
    """
    Read parameters from a file and return the data.
    """
    params = ""
    try:
        with open(file_path, 'r') as f:
            params = f.read()
            logger.info(f"Successfully read from {file_path}")
            return params
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return None
    except PermissionError:
        logger.error(f"Error: You do not have permission to access this file: {file_path}")
        return None
    except IOError as e:
        logger.error(f"An I/O error occurred: {file_path}")
        return None
    except Exception as e:        
        logger.error(f"Failed to read from {file_path}: {e}")
        return None
        
    return params


if __name__ == "__main__":
    
    arg1 = "" 
    if len(sys.argv) < 2:
        logger.error("No file path provided. Please provide a file path as a command line argument.")
        sys.exit(1)
    for i, arg in enumerate(sys.argv[1:]):
        logger.info(f"Argument {i+1}: {arg}")
        arg1 = arg

    params = read_params(arg1)
    if params is None:
        logger.error("Failed to read parameters from the file.")
        sys.exit(1)

    param_data = json.loads(params)  # Assuming the file contains JSON data
    start_date = param_data['date_range']['start']
    end_date = param_data['date_range']['end']
    comids = param_data['comids']
    if len(comids) == 0:
        logger.error("No COMIDs provided in the input file.")
        sys.exit(1)
    file_name = param_data['file_name']
    _, file_extension = os.path.splitext(file_name)
    if file_extension != ".csv":
        file_name = file_name + ".csv"
        

    get_data(start_date, end_date, comids, file_name)

    logger.info(f"Successfully wrote results to: {file_name}")