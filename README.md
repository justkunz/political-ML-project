political-ML-project
====================

This repo holds my EECS 598 - Practical Machine Learning class.
The goal of this project is to apply machine learning to 
Michigan politician information in order to get useful insights,
like which politicians feel the same way about political issues.

Script Run Order:

data_loading/vote_smart.py
data_loading/political_websites.py
preprocessing/merge_data.py
preprocessing/preprocess_data.py
preprocessing/prune_by_tf_idf.py --remove 35
preprocessing/prepare_for_hdp.py

Run Mallet:
======

Turn the data into Mallet Format
====
/Applications/mallet/bin/mallet import-file --label 0 --name 1 --data 2 --input ../../data/preprocessing/topic_model_data.csv --output ../../data/mallet/data.mallet --keep-sequence-bigrams

Run the Topic Modeling
====
/Applications/mallet/bin/mallet train-topics --input ../../data/mallet/data.mallet --output-topic-keys ../../data/mallet/topic_keys.txt --output-doc-topics ../../data/mallet/topic_composition.txt --num-topics 10 --use-ngrams true

Run the HLDA
====
The input instances must be FeatureSequence or FeatureSequenceWithBigrams, not FeatureVector

/Applications/mallet/bin/mallet import-file --label 0 --name 1 --data 2 --input ../../data/preprocessing/topic_model_data.csv --output ../../data/mallet/hlda_data.mallet --keep-sequence-bigrams
/Applications/mallet/bin/mallet hlda --input ../../data/mallet/hlda_data.mallet


--use-ngrams true|false?
