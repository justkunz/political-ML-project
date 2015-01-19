from pandas import DataFrame, Series
import pandas as pd
import logging
import nltk


def get_unique_tokens(corpusFrame):
  """Tokenize the data set into a set of unique words"""
  token_set = set()
  for index, row in corpusFrame.iterrows():
    tokens = nltk.word_tokenize(row["text"])
    token_set = token_set.union(set(tokens))

  #logging.info("Found %d unique token words in %d documents", len(token_set), len(corpusFrame))
  return token_set


def get_tokens(corpusFrame):
  """Tokenize the data set into an list of words found in the corpusFrame"""
  token_list = []
  for index, row in corpusFrame.iterrows():
    tokens = nltk.word_tokenize(row["text"])
    token_list.append(tokens)

  #logging.info("Found %d total token words in %d documents", len(token_list), len(corpusFrame))
  return token_list
