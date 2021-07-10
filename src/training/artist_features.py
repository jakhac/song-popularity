import pandas as pd
import numpy as np

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import List

load_dotenv()
DATA_PATH = Path(os.getenv("DATA_PATH"))

# only for .ipynb because relative imports don't work
root_path = DATA_PATH.parent
os.chdir(str(root_path))

import src.training.pre_training as t
import src.training.postprocessing as pp

from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import RandomOverSampler
from sklearn.metrics import plot_confusion_matrix

# sklearn imports
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

# # Preprocessing

# ## Load Data
df = t.get_artist_df()

# scaling
max_followers = df["followers"].max()
df["followers"] = df["followers"].apply(lambda x: x / (max_followers / 100))
df["genre_name"] = df["genre_name"].apply(t.encode_genres)


# ## Split data (X,y)
y = df["popularity"].apply(t.encode_popularity)
X = df.values[:, :2]

# print(X)
# print(y)


# ## Over-/Undersampling
# sampled and encoded popularity
X, y = RandomUnderSampler(random_state=42).fit_resample(X, y)
# X, y = RandomOverSampler(random_state=42).fit_resample(X, y)


# Plot distr
fig = plt.figure(figsize=(5, 5))
ax = fig.add_subplot(111)
ax.set_title("pop distr")
ax.set_xlabel("popularity")
ax.set_ylabel("count")

plt.bar(list(set(y)), pp.count_distribution(y))

# print(pd.DataFrame(y).value_counts())


# ## Train/Test-Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(X_train.shape)
print(X_test.shape)


# # Classification

# ## Gaussian Naive Bayes
print("Gaussian Naive Bayes")
gaussian_clf = GaussianNB()

# fit the model
gaussian_clf.fit(X_train, y_train)

pp.print_metrics(gaussian_clf, X_test, y_test)


# ## SVM
print("SVC")
svc_clf = SVC()

# fit the model
svc_clf.fit(X_train, y_train)

pp.print_metrics(svc_clf, X_test, y_test)


# ## Neural Network
print("Neural Network")
nn_clf = MLPClassifier()

# fit the model
nn_clf.fit(X_train, y_train)

pp.print_metrics(nn_clf, X_test, y_test)


# ## K-Neighbours Classifier
print("K-Neighbours Classifier")
knn_clf = KNeighborsClassifier()

# fit the model
knn_clf.fit(X_train, y_train)

pp.print_metrics(knn_clf, X_test, y_test)


# ## Decision Trees
print("Decision Trees")
dt_clf = DecisionTreeClassifier()

# fit the model
dt_clf.fit(X_train, y_train)

pp.print_metrics(dt_clf, X_test, y_test)


# ## Random forest
# use different number of trees in forest (comparing different hyperparameters)
forest_size = [10, 20, 50, 100]

# set seed for random state to get compareable results in every execution (forest randomness)
np.random.seed(500)

for trees in forest_size:
    # set forest size
    print("Predicting with forest size " + str(trees))
    rf = RandomForestClassifier(n_estimators=trees)

    # fit the model
    rf.fit(X_train, y_train)

    pp.print_metrics(rf, X_test, y_test)
    print("--------\n")


# # Model Evaluation

# ## Plotting
import matplotlib.pyplot as plt

plt.title("Dataset Artists V1 + unpredicted popularity")
plt.xlabel("popularity")
plt.ylabel("artist count")

plt.bar(list(set(y_test)), pp.count_distribution(y_test))
plt.show()


# Confusion matrix
fig, cax = plt.subplots(figsize=(16, 16))  # subplot for larger size
# plot_confusion_matrix(estimator=knn_clf, X=X_test, y_true=y_test, cmap=plt.cm.Blues,normalize="true",values_format=".2f",ax=cax)
plot_confusion_matrix(
    estimator=knn_clf,
    X=X_test,
    y_true=y_test,
    cmap=plt.cm.Blues,
    normalize=None,
    values_format=".2f",
    ax=cax,
)

plt.show()
