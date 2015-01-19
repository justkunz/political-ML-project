from config import MERGED_DATA_PATH, TOPIC_MODEL_DATA_PATH, SENTIMENT_MODEL_DATA_PATH, POLITICAL_JARGON_PATH
from config import TEXT_COL, POLITICIAN_COL
from pandas import DataFrame, Series
from sentiment_analysis import SentimentAnalysis
import pandas as pd
from stemming.porter2 import stem as stem_fn
import string
import logging
import utils
from collections import Counter
from argparse import ArgumentParser
from sklearn.feature_extraction.text import TfidfVectorizer
logging.basicConfig(level=logging.DEBUG)
import csv


from nltk.corpus import stopwords
from nltk import word_tokenize

stem_dictionary = {}

LABEL_COL = "politician_label"

def stem(word):
  stemmed_word = stem_fn(word)
  if len(stemmed_word) == 0:
    return ""
    
  if stemmed_word in stem_dictionary:
    stem_dictionary[stemmed_word].append(word)
  else:
    stem_dictionary[stemmed_word] = [word]
  return stemmed_word

def unstem(stemmed_word):
  c = Counter(stem_dictionary[stemmed_word])
  word, count = c.most_common(1)[0]
  return word


def get_political_jargon():
  jargon_file = open(POLITICAL_JARGON_PATH, "r")
  results = jargon_file.read()
  results = "".join([letter.lower() for letter in results])
  results = word_tokenize(results)
  results = [stem(word) for word in results]
  return results


def simple_preprocessing(merged_data):
  political_jargon = get_political_jargon()
  
  # remove any unicode characters
  merged_data[TEXT_COL] = merged_data[TEXT_COL].apply(lambda text: text.decode("utf-8", "ignore"))
  merged_data[TEXT_COL] = merged_data[TEXT_COL].apply(lambda text: text.encode("ascii","ignore"))

  # remove punctuation
  logging.debug("Removing all punctuation")
  merged_data[TEXT_COL] = merged_data[TEXT_COL].apply(lambda text: text.translate(string.maketrans("",""), string.punctuation))
  
  # make all of the strings lower case
  logging.debug("Casting all chars to lower case")
  merged_data[TEXT_COL] = merged_data[TEXT_COL].apply(lambda text: text.lower())
  
  # tokenize all of the words
  logging.debug("Tokenizing the words")
  merged_data[TEXT_COL] = merged_data[TEXT_COL].apply(lambda text: " ".join([word for word
    in word_tokenize(text)]))
  
  # remove numbers
  logging.debug("Removing all numbers")
  merged_data[TEXT_COL] = merged_data[TEXT_COL].apply(lambda text: "".join([digit for digit in text if not digit.isdigit()]))

  # remove the stop words
  logging.debug("Removing all stopwords")
  merged_data[TEXT_COL] = merged_data[TEXT_COL].apply(lambda text: " ".join([word for word
    in text.split() if word not in stopwords.words("english")]))

  # stem all of the terms
  logging.debug("Stemming all of the words")
  merged_data[TEXT_COL] = merged_data[TEXT_COL].apply(lambda text: " ".join([stem(word) for word in text.split()]))
  
  # remove any political jargon terms
  logging.debug("Removing all political jargon")
  merged_data[TEXT_COL] = merged_data[TEXT_COL].apply(lambda text: " ".join([word for word
    in text.split() if word not in political_jargon]))
  
  # change the spaces to underscores in the politician names
  merged_data[POLITICIAN_COL] = merged_data[POLITICIAN_COL].apply(lambda text: text.replace(" ", "_"))
  
  # un-stem the words (necessary for the sentiment analysis)
  logging.debug("Unstemming all of the words")
  merged_data[TEXT_COL] = merged_data[TEXT_COL].apply(lambda text: " ".join([unstem(word) for word
    in text.split()]))

  return merged_data


def apply_sentiments(corpusFrame):
  s = SentimentAnalysis()
  corpusFrame = s.assign_document_sentiment(corpusFrame, TEXT_COL)
  corpusFrame[TEXT_COL] = corpusFrame[TEXT_COL].apply(lambda text: s.strip_sentiment(text))

  return corpusFrame


def remove_high_tf_idf(corpusFrame, num_to_remove):
  """ Remove the top num_to_remove terms by tf idf"""
  
  if num_to_remove == 0:
    return corpusFrame
  
  tokens = utils.get_unique_tokens(corpusFrame)
  token_size_before = len(tokens)
  
  logging.debug("Starting the process of pruning %d freqent terms out of %d", num_to_remove, token_size_before)

  # compute the TF-IDF scores for all the text
  tfidf = TfidfVectorizer(tokenizer=word_tokenize)
  tfs = tfidf.fit_transform(corpusFrame[TEXT_COL])
  
  #tfs = tfidf.fit_transform(["".join(corpusFrame[TEXT_COL].values)])
  feature_names = tfidf.get_feature_names()

  # sum the TF-IDF scores 
  word_scores = tfs.sum(axis=0).getA()[0]

  # remove the most common words from the corpus
  removal_indices = word_scores.argsort()[-1:(-1*num_to_remove-1):-1]
  removal_words = [feature_names[index] for index in removal_indices]
  logging.info("Removing %d words", len(removal_words))
  logging.debug(removal_words)
  
  corpusFrame[TEXT_COL] = corpusFrame[TEXT_COL].apply(lambda text: " ".join(word for word in word_tokenize(text) if word not in removal_words))

  tokens_after = utils.get_unique_tokens(corpusFrame)
  logging.info("Removed %d tokens", (token_size_before - len(tokens_after)))
  return corpusFrame


def add_label(corpusFrame):
  POLITICIANS = {"Terri_Lynn_Land": "R", "Rick_Snyder": "R", "Bill_Schuette":"R",
    "Ruth_Johnson":"R", "Gary_Peters":"D", "Mark_Schauer":"D", "Mark_Totten":"D", "Godfrey_Dillard":"D"}

  for index in range(len(corpusFrame)):
    corpusFrame.loc[index, LABEL_COL] = POLITICIANS[corpusFrame.loc[index, 'politician']]
    
  return corpusFrame


def main(remove_idf):
  """Preprocess the text features, remove punctuation, stop words, and political
  jargon. Save the final processed DataFrame."""

  # load the merged DataFrame
  merged_data = pd.read_csv(MERGED_DATA_PATH)
  logging.info("Read %d records from %s", len(merged_data), MERGED_DATA_PATH)
  
  # do some simple preprocessing (remove stopwords, punctuation, etc)
  merged_data = simple_preprocessing(merged_data)
  
  # assign sentiment scores to the documents and remove any sentiment labels
  merged_data = apply_sentiments(merged_data)
  
  # remove words with high term frequency and document frequency
  #merged_data = remove_high_tf_idf(merged_data, remove_idf)
  
  logging.info("Final preprocessed text data has %d unique tokens", len(utils.get_unique_tokens(merged_data)))
  
  merged_data = add_label(merged_data)
  
  merged_data[[POLITICIAN_COL, LABEL_COL, TEXT_COL]].to_csv(TOPIC_MODEL_DATA_PATH, index=False, header=False, sep=" ")
  logging.info("Saved %d topic model data records to %s", len(merged_data), TOPIC_MODEL_DATA_PATH)
  
  merged_data.to_csv(SENTIMENT_MODEL_DATA_PATH, index=False)
  logging.info("Saved %d sentiment model data records to %s", len(merged_data), SENTIMENT_MODEL_DATA_PATH)

  # saved the stem dictionary
  w = csv.writer(open("../../data/processed/stem_dictionary.csv", "w"))
  for key, val in stem_dictionary.items():
    w.writerow([key, val])
  

if __name__ == '__main__':
  # the command line takes one arg, --remove, to indicate the number of frequent terms to remove
  parser = ArgumentParser(description="Remove words from the corpus with high term frequency")
  parser.add_argument("--remove", type=int,
                     help="The number of frequent terms to remove from the corpus",
                     default=20)
  args = parser.parse_args()

  main(args.remove)

