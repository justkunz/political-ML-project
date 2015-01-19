from config import POLITICIANS, DATA_FILEPATH, TEXT_KEY, POLITICIAN_KEY
import re
import glob
from pandas import DataFrame, Series
from progressbar import ProgressBar
import logging
logging.basicConfig(level=logging.DEBUG)


WEBSITE_TEXT_PATH = DATA_FILEPATH + "political_websites/"
RESULTS_FILE = WEBSITE_TEXT_PATH + "scrape_results.csv"

def main():

  results = DataFrame()
  
  # loop through the data files and create one DataFrame of information
  file_list = glob.glob(WEBSITE_TEXT_PATH + "*.txt")
  for filename in file_list:
  
    # extract the politician name from the file name (be careful of 3 name politicians)
    match = re.search('([a-zA-Z]+ [a-zA-Z]+[ a-zA-Z]*)\.txt$', filename)
    politician = match.group(1)

    file_obj = file(filename)
    text = file_obj.read()
    
    # split the text by paragraph
    paragraphs = text.split("\n")

    for p in paragraphs:
      if len(p) == 0:
        continue
      results = results.append({TEXT_KEY: p,  POLITICIAN_KEY: politician},
        ignore_index=True)
  

  results.to_csv(RESULTS_FILE, index=False)
  logging.info("Saved %d political website records to %s", len(results), RESULTS_FILE)


main()