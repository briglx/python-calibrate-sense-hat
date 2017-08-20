#!/usr/bin/python

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

names = ['direction', 'pitch', 'roll', 'yaw']
df = pd.read_csv("rawsample-munged.csv", names=names, header=0)

# Split Test from training set
df['is_train'] = np.random.uniform(0, 1, len(df)) <= .75
train, test = df[df['is_train']==True], df[df['is_train']==False]
features = df.columns[1:4]

# Factorize class names to numbers
y, target_names = pd.factorize(train['direction'])

# Train
clf = RandomForestClassifier(n_jobs=2)
clf.fit(train[features], y)

# Score
preds = target_names[clf.predict(test[features])]
confusionmatrix = pd.crosstab(test['direction'], preds, rownames=['actual'], colnames=['preds'])
print confusionmatrix

precision =  pd.Series(np.diag(confusionmatrix / confusionmatrix.sum(0) ).round(2), index=["Bottom", "Left", "Right", "Top"])
print precision

recall = pd.Series(np.diag(confusionmatrix / confusionmatrix.sum(1)).round(2), index=["Bottom", "Left", "Right", "Top"])
print recall

f1score = 2 * (precision * recall) / (precision + recall)
print f1score

gscore =np.sqrt(precision * recall)
print gscore