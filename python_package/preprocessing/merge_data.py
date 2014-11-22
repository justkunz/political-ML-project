from config import MERGED_DATA_PATH
from pandas import DataFrame, Series
import pandas as pd
import logging
logging.basicConfig(level=logging.DEBUG)

DATA_PATH = "../../data/"
DATA_SOURCES = ["vote_smart/scrape_results.csv"]

def main():

  merged_data = DataFrame()
  
  # loop through all of the data sources and append one large DataFrame
  for data_file in DATA_SOURCES:
    merged_data = merged_data.append(pd.read_csv(DATA_PATH + data_file))

  # save the merged result to the preprocessing folder
  merged_data.to_csv(MERGED_DATA_PATH)

  logging.info("Saved %d merged records to %s", len(merged_data), MERGED_DATA_PATH)


main()
