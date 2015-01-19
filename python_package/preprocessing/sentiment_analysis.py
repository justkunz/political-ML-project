import subprocess
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import utils
import logging
import unirest
from progressbar import ProgressBar

from config import SENTIMENT_WORD_ASSIGNMENTS_PATH

word_col = 'word'
pos = 'pos'
neutral = 'neutral'
neg = 'neg'
label = 'label'
score = 'Sentiment Score'
probability = 'probability'

class SentimentAnalysis:

  def __init__(self):
    self.load_assignments()

  def assign_document_sentiment(self, corpusFrame, text_col):
    """For each document (row) assign a sentiment label (pos, neg, neutral) and a score, based
       on the words in the document"""
    
    pbar = ProgressBar(maxval=len(corpusFrame)).start()
    
    corpusFrame[pos] = 0
    corpusFrame[neg] = 0
    corpusFrame[neutral] = 0
    corpusFrame[label] = neutral
    
    for index, row in corpusFrame.iterrows():
      self.compute_document_assignment(corpusFrame, index, text_col)
      pbar.update(index+1)
    
    # scale the scores to have a std = 1
    mean_val = corpusFrame[score].mean()
    std_val = corpusFrame[score].std()
    corpusFrame[score] = (corpusFrame[score] - mean_val)/std_val

    logging.info("Found %d positive documents", len(corpusFrame[corpusFrame[label] == pos]))
    logging.info("Found %d negative documents", len(corpusFrame[corpusFrame[label] == neg]))
    
    print corpusFrame.head()

    return corpusFrame


  def compute_document_assignment(self, corpusFrame, index, text_col):
    '''Compute the sentiment label (pos/neg) for the document at corpusFrame[index, text_col].
    The labels are computed using the following criteria:
      Loop through all the words in the document
        If the word is positive, increment the sentiment score by the positive weight
        Elif the word is negative, decrement the sentiment score by the negative weight
    '''
    '''
    pos_scores = []
    neg_scores = []
    
    # load the scores for all of the words in the document
    for word in corpusFrame.loc[index, text_col].split():
    
      # load the word sentiment assignment if it has not yet been fetched
      word_assignment = self.fetch_or_load_assignment(word)
      
      # only count the positive/negative for non-neutral words
      if word_assignment[label].values == pos:
        pos_scores.append(word_assignment[pos].values[0])
      elif word_assignment[label].values == neg:
        neg_scores.append(word_assignment[neg].values[0])

    # average the scores for the whole document
    avg_pos, avg_neg = np.mean(pos_scores), np.mean(neg_scores)
    
    # append the scores to the document row
    corpusFrame.loc[index, pos] = avg_pos
    corpusFrame.loc[index, neg] = avg_neg
  
    # classify the document as positive or negative
    if (avg_pos > avg_neg):
      corpusFrame.loc[index, label] = pos
    else:
      corpusFrame.loc[index, label] = neg
    '''
    sentiment_score = 0
    # load the scores for all of the words in the document
    for word in corpusFrame.loc[index, text_col].split():
    
      # load the word sentiment assignment if it has not yet been fetched
      word_assignment = self.fetch_or_load_assignment(word)
      
      # only count the positive/negative for non-neutral words
      if word_assignment[label].values == pos:
        sentiment_score = sentiment_score + word_assignment[pos].values[0]
      elif word_assignment[label].values == neg:
        sentiment_score = sentiment_score - word_assignment[neg].values[0]
      
    corpusFrame.loc[index, score] = sentiment_score
    
    # classify the document as positive or negative
    if (sentiment_score > 0):
      corpusFrame.loc[index, label] = pos
    else:
      corpusFrame.loc[index, label] = neg
    
    return corpusFrame

  def fetch_or_load_assignment(self, word):
  
    # check if the word assignment has already been loaded
    if len(self.assignments[self.assignments[word_col] == word]) == 0:
      logging.debug("Missing sentiment assignment for %s", word)
      self.assignments = self.assignments.append(self.scrape_nltk(word))
      self.save_assignments()
    
    word_assignment = self.assignments[self.assignments[word_col] == word]
    assert (len(word_assignment) == 1)
    word_assignment = word_assignment[:1]
    return word_assignment


  def strip_sentiment(self, text):
    # remove any words with positive/negative sentiment labels (aka keep only neutral words)
    neutral_words = self.assignments[self.assignments[label] == neutral][word_col].values
    new_text = " ".join([word for word in text.split() if word in neutral_words])
    return new_text


  def load_assignments(self):
    """Get the sentiment assignments in a DataFrame"""
    self.assignments = pd.read_csv(SENTIMENT_WORD_ASSIGNMENTS_PATH)
    logging.info("Loaded %d assignments from %s", len(self.assignments), SENTIMENT_WORD_ASSIGNMENTS_PATH)
  
  
  def save_assignments(self):
    self.assignments.to_csv(SENTIMENT_WORD_ASSIGNMENTS_PATH, index=False)
    logging.info("Saved %d assignments to %s", len(self.assignments), SENTIMENT_WORD_ASSIGNMENTS_PATH)


  def scrape_nltk(self, word):
    """Get the sentiment assignment for this word""" 

    response = unirest.post("https://japerk-text-processing.p.mashape.com/sentiment/",
      headers={
        "X-Mashape-Key": "XoGF6IDzdymshmEOOTXVoIyc0eysp14CvaZjsnG8vbdTzEGIiM",
        "Content-Type": "application/x-www-form-urlencoded"
      },
      params={
        "language": "english",
        "text": word
      }
    )
    assignment = response.body
    formatted_assignment = DataFrame({'word': word, pos:assignment[probability][pos],
                                      neg:assignment[probability][neg], neutral:assignment[probability][neutral],
                                      label:assignment[label]}, index=[1])
      
    return formatted_assignment
