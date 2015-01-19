from config import POLITICIANS, DATA_FILEPATH, TEXT_KEY, POLITICIAN_KEY
import json
import urllib
import re
from pandas import DataFrame, Series
from progressbar import ProgressBar
import logging
logging.basicConfig(level=logging.DEBUG)

TITLE_KEY = "title"

VOTE_SMART_PATH = DATA_FILEPATH + "vote_smart/"
HREF_FILE = VOTE_SMART_PATH + "politician_issue_links.txt"
RESULTS_FILE = VOTE_SMART_PATH + "scrape_results.csv"


def get_formatted_row(json_result):

  try:
    results = json_result["results"]
  except KeyError as e:
    logging.debug(json_result)
    logging.warning(e)
    return DataFrame()
    
  try:
    # parse the issue title
    issue_title = results["collection2"][0][TITLE_KEY]
  
    # parse the text from the issue statement
    issue_text = [row[TEXT_KEY] for row in results["collection1"]]
  
  except KeyError as e:
    logging.warning(e)
    logging.debug(results.keys())
    logging.debug(results)
    return DataFrame()

  try:
    issue_text = " ".join(issue_text)
    issue_text = issue_title + " " + issue_text
  except TypeError as e:
    logging.warning(e)
    
  # parse the contributors (only consider contributors in the politicians list)
  contributors = [row[POLITICIAN_KEY]["text"] for row in results["collection3"]]
  contributors = [contributor for contributor in contributors if contributor in POLITICIANS.values]

  assert(len(contributors) > 0)
  
  pd_result = DataFrame()

  # add an entry for each contributor
  for contributor in contributors:
    pd_result = pd_result.append({TEXT_KEY: issue_text, \
      POLITICIAN_KEY: contributor}, ignore_index=True)

  assert(len(pd_result) == len(contributors))
  return pd_result


def scrape_kimono_labs():
  # open the file with the hrefs to scrape
  num_lines = sum([1 for line in open(HREF_FILE)])
  href_file = open(HREF_FILE, 'r')
  
  # store the results in a DataFrame
  results_table = DataFrame()
  
  pbar = ProgressBar(maxval=num_lines).start()
  
  for i in range(num_lines):
    href = href_file.readline()
    # get the url parameters from the href for the API call
    match = re.search('http://votesmart.org/public-statement/(\d+)/(.+)', href)
    kimpath2 = match.group(1)
    kimpath3 = match.group(2)
  
    try:
      scrape_href = "https://www.kimonolabs.com/api/dr3xxfom?" \
        + "apikey=uJtZym147qhHh0poD2oh0dqNkjaVs7Y4" \
        + "&kimpath1=public-statement&kimpath2=" + str(kimpath2) \
        + "&kimpath3=" + kimpath3
    
      # get the vote smart results from the Kimono Labs api
      # and append them to the DataFrame
      raw_results = json.load(urllib.urlopen(scrape_href))
      results_table = results_table.append(get_formatted_row(raw_results))

    except ValueError:
      logging.warning("Unable to get results for: " + href)
  
    pbar.update(i+1)

  pbar.finish()
  return results_table

def main():
    
  # reformat the contributors column
  issues_table = scrape_kimono_labs()

  # save the results to a file
  issues_table.to_csv(RESULTS_FILE, encoding="utf-8", index=False)
  logging.info("Saved %d scraped vote smart records to %s", len(issues_table), RESULTS_FILE)
  

main();
