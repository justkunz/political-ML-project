from config import MERGED_DATA_PATH, CLEANED_DATA_PATH, POLITICAL_JARGON_PATH
from pandas import DataFrame, Series
import pandas as pd
import string
import logging
logging.basicConfig(level=logging.DEBUG)

from nltk.corpus import stopwords

def get_political_jargon():
  jargon_file = open(POLITICAL_JARGON_PATH, "r")
  results = jargon_file.read()
  results = "".join([letter.lower() for letter in results])
  return results.split("\n")

def main():
  """Preprocess the text features, remove punctuation, stop words, and political
  jargon. Save the final processed DataFrame."""

  # load the merged DataFrame
  merged_data = pd.read_csv(MERGED_DATA_PATH)
  logging.info("Read %d records from %s", len(merged_data), MERGED_DATA_PATH)

  political_jargon = get_political_jargon()
  
  # preprocess the two text columns
  for col in ["text", "title"]:
  
    # make all of the strings lower case
    merged_data[col] = merged_data[col].apply(lambda text: text.lower())
    
    # remove punctuation
    merged_data[col] = merged_data[col].apply(lambda text: text.translate(string.maketrans("",""), string.punctuation))
    
    # remove numbers
    merged_data[col] = merged_data[col].apply(lambda text: "".join([digit for digit in text if not digit.isdigit()]))
  
    # remove the stop words
    merged_data[col] = merged_data[col].apply(lambda text: " ".join([word for word
      in text.split() if word not in stopwords.words("english")]))
  
    # remove any political jargon terms
    merged_data[col] = merged_data[col].apply(lambda text: " ".join([word for word
      in text.split() if word not in political_jargon]))
  
  merged_data.to_csv(CLEANED_DATA_PATH, index=False)
  logging.info("Saved cleaned data to %s", CLEANED_DATA_PATH)

main()