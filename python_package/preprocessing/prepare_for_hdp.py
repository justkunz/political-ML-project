"""Process the data into the format necessary for the HDP algorithm"""
from config import SECOND_CLEANED_DATA_PATH, HDP_DATA_PATH, VOCABULARY_DATA_PATH
from pandas import DataFrame, Series
import pandas as pd
import string
import logging
import nltk
import utils
logging.basicConfig(level=logging.DEBUG)


def create_vocabulary(corpusFrame):
  """Create a dictionary to hold the vocabulary of the corpus. 
    Args: 
      corpusFrame(DataFrame): the DataFrame holding all of the text documents
    Returns: (dictionary)
  """
  # collect the set of tokens from all documents
  tokens = utils.get_unique_tokens(corpusFrame)
  #print sorted(tokens, key=lambda item: (int(item.partition(' ')[0]) if item[0].isdigit() else float('inf'), item))

  # assign word ids to all the tokens
  vocabulary = {word : wordid for wordid, word in enumerate(tokens)}

  # save the vocab to a file
  with open(VOCABULARY_DATA_PATH, "w") as f:
      for (word, word_id) in vocabulary.iteritems():
        f.write(word + ":" + str(word_id) + "\n")
        
  logging.info("Saved a vocabulary with %d distinct words to %s", len(vocabulary), VOCABULARY_DATA_PATH)
  return vocabulary


def get_hdp_formatted_documents(corpusFrame, vocabulary):
  """Return a list formatted as [[totalWords:word1id:word1count:word2id:word2count...\n],  ]"""
  document_counts = []
  # loop through documents
  for index, row in corpusFrame.iterrows():
    word_counts = {}
    # loop through all the text
    for word in nltk.word_tokenize(row["text"]):
      if word in word_counts:
        word_counts[word] = word_counts[word] + 1
      else:
        word_counts[word] = 1
  
    # turn the word count dictionary into the string [word1id: ...]
    id_string = [str(vocabulary[word]) + ":" + str(word_counts[word]) for word in word_counts]

    id_string = ":".join(id_string)
    id_string = id_string + "\n"
  
    #insert the unique total word count at the 0 index
    id_string = str(len(word_counts)) + ":" + id_string
    document_counts.append(id_string)
  return document_counts

def main():
  """
  Each line of the corpus should be formatted [<Some num> :word1id :word1count: ...]
    splitexp = re.compile(r'[ :]')
    wordids = splitline[1::2]
    wordcts = splitline[2::2]
    d.words = wordids
    d.counts = wordcts
  """

  cleaned_data = pd.read_csv(SECOND_CLEANED_DATA_PATH)

  vocabulary = create_vocabulary(cleaned_data)

  hdp_data_list = get_hdp_formatted_documents(cleaned_data, vocabulary)
  with open(HDP_DATA_PATH, "w") as f:
    for line in hdp_data_list:
        f.write(line)
  
  logging.info("Saved %d hdp formatted documents to %s", len(hdp_data_list), HDP_DATA_PATH)

if __name__ == '__main__':
  main()

# python run_hdp.py --data_path="../data/preprocessing/hdp_data.txt" --D=194 --W=5227
