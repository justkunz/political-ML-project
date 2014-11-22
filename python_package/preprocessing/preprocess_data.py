from config import MERGED_DATA_PATH
from pandas import DataFrame, Series
import pandas as pd
import logging
logging.basicConfig(level=logging.DEBUG)

from nltk.corpus import stopwords

def remove_stopwords(string):
  return "".join([string for string in text.split()
    if string not in stopwords.words("english")])

def main():
  """Preprocess the text features, remove punctuation, stop words, and political
  gargin. Save the final processed DataFrame."""

  # load the merged DataFrame
  merged_data = pd.read_csv(MERGED_DATA_PATH)
  logging.info("Read %d records from %s", len(merged_data), MERGED_DATA_PATH)

  # preprocess the two text columns
  for col in ["text", "title"]:
  
    # make all of the strings lower case
    merged_data[col] = merged_data[col].apply(lambda text: text.lower())
    
    # TODO: remove punctuation
    # TODO: remove numbers
  
  
  
    # remove the stop words from the title and text
    merged_data[col] = merged_data[col].apply(lambda string: " ".join([word for word
      in string.split() if word not in stopwords.words("english")]))
  


main()