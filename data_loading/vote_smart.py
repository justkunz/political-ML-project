import json
import urllib
import re
from pandas import DataFrame, Series
from progressbar import ProgressBar
import logging
logging.basicConfig(level=logging.DEBUG)

# TODO: make this less hard-coded
#from . import POLITICIANS
POLITICIANS = Series(["Terri Lynn Land", "Rick Snyder", "Bill Schuette", "Ruth Johnson", "Gary Peters", "Mark Schauer", "Mark Totten", "Godfrey Dillard"])

TEXT_KEY = "text"
POLITICIAN_KEY = "politician"
TITLE_KEY = "title"

DATA_FILEPATH = "../data/vote_smart/"
HREF_FILE = DATA_FILEPATH + "politician_issue_links.txt"
RESULTS_FILE = DATA_FILEPATH + "scrape_results.csv"


def get_formatted_row(json_result):

  results = json_result["results"]
  
  # parse the issue title
  try:
    issue_title = results["collection2"][0][TITLE_KEY]
  except KeyError as e:
    logging.warning(e.strerror)
    return DataFrame()

  # parse the text from the issue statement
  issue_text = [row[TEXT_KEY] for row in results["collection1"]]
  issue_text = "".join(issue_text)

  # parse the contributors (only consider contributors in the politicians list)
  contributors = [row[POLITICIAN_KEY]["text"] for row in results["collection3"]]
  contributors = [contributor for contributor in contributors if contributor in POLITICIANS.values]
  
  pd_result = DataFrame()

  # add an entry for each contributor
  for contributor in contributors:
    pd_result = pd_result.append({TITLE_KEY: issue_title, TEXT_KEY: issue_text, \
      POLITICIAN_KEY: contributor}, ignore_index=True)

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
  
    # TODO: remove this
    results_table.to_csv(RESULTS_FILE, encoding="utf-8")
  
    pbar.update(i+1)

  pbar.finish()
  return results_table

def main():
    
  # reformat the contributors column
  issues_table = scrape_kimono_labs()

  issues_table.to_csv(RESULTS_FILE)
  

main();
