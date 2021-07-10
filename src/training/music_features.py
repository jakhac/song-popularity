import os
import sys
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from dotenv import load_dotenv
from imblearn.over_sampling import RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler

load_dotenv()

DATA_PATH = Path(os.getenv("DATA_PATH"))

# only for .ipynb because relative imports don't work
# root_path = DATA_PATH.parent
# os.chdir(str(root_path))
# print(root_path)

from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import plot_confusion_matrix
from sklearn.model_selection import train_test_split

# import models
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from .plotting import generate_model_plots, plots_from_list
from .postprocessing import print_metrics
from .pre_training import encode_popularity, get_music_df


# # Preprocessing
def train():
    # ## Load Data
    df = get_music_df()
    print(df.shape)

    # df2 = get_lyric_df()
    # df = df1.join(df2, on='song_id')
    # df = df1.merge(df2, 'ts.song_id')

    # ## Split data (X,y)
    # Split data into sample values and sample classes

    X = df.values[:, :15]
    y = df["popularity"].apply(encode_popularity)

    # X = df[["explict", "danceability", "energy", "loadness", "mode", "speechiness", "acousticness", "instrumentalness", "liveness", "valence"]]
    # X = df[["danceability", "energy", "loadness"]]

    # ## Over-/Undersampling
    # sampled and encoded popularity
    # X, y = RandomUnderSampler(random_state=42).fit_resample(X, y)

    # # ## PCA
    # # Dimensionality Reduction
    # reduce_to = 15

    # # PCA feature selection (TODO what does this do?)
    # cols = pd.DataFrame(X).columns

    # # Standardization of X
    # scaler = StandardScaler()
    # scaler.fit(X)
    # X = scaler.transform(X)

    # # apply PCA to X
    # pca = PCA(n_components=reduce_to)
    # pca.fit(X, y)
    # X = pca.transform(X)

    # print("Amount explained:", sum(pca.explained_variance_ratio_))
    # print("Amount explained in each PC:", pca.explained_variance_ratio_)

    # descr = ["PC-" + str(x) for x in range(1, reduce_to + 1)]
    # print(pd.DataFrame(pca.components_, columns=cols, index=descr))

    # ## Feature Selection
    # # Pearson Correlation Coefficient
    # pear_corr = df.corr(method="pearson")
    # plt.imshow(pear_corr, cmap="hot")
    # plt.show()

    # TODO copy this to plotting notebook, plot only after PCA/feature selection here
    # TODO use correct X, y values
    # X_1, y_1 = RandomUnderSampler(random_state=42).fit_resample(df, y)

    # # Scale features
    # max_db = X_1['loadness'].max()
    # min_db = X_1['loadness'].min()
    # X_1['loadness'] = X_1['loadness'].apply(lambda x: abs(x/40))

    # # Drop features with range outside [0, 1]
    # X_1 = pd.DataFrame(X_1).drop(['key', 'time_signature', 'release_year', 'duration_ms', 'tempo'], axis=1)

    # fig = plt.figure(figsize = (20, 25))
    # j = 0
    # for i in pd.DataFrame(X_1).columns:
    #     plt.subplot(6, 4, j+1)
    #     j += 1

    #     sns.kdeplot(pd.DataFrame(X_1).query("popularity == 0")[i], color='b', label='pop=0')
    #     sns.kdeplot(pd.DataFrame(X_1).query("popularity == 1")[i], color='#000000', label='pop=1')
    #     sns.kdeplot(pd.DataFrame(X_1).query("popularity == 2")[i], color='#ff5959', label='pop=2')
    #     sns.kdeplot(pd.DataFrame(X_1).query("popularity == 3")[i], color='#fffd86', label='pop=3')
    #     sns.kdeplot(pd.DataFrame(X_1).query("popularity == 4")[i], color='#a7e81c', label='pop=4')
    #     sns.kdeplot(pd.DataFrame(X_1).query("popularity == 5")[i], color='#65bf65', label='pop=5')
    #     plt.legend(loc='best')
    #     plt.ylim(0, 17)
    #     plt.xlim(0, 1)

    # fig.suptitle('Density Analysis')
    # fig.tight_layout()
    # fig.subplots_adjust(top=0.95)
    # plt.show()

    # ## Train/Test-Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(X_train.shape)
    print(X_test.shape)

    # # Classification
    # store classifiers for later plotting
    clf_list = []

    # ## Gaussian Naive Bayes
    gaussian_clf = GaussianNB()

    # fit the model
    gaussian_clf.fit(X_train, y_train)
    clf_list.append(gaussian_clf)

    print_metrics(gaussian_clf, X_test, y_test)

    # ## SVM
    # svc_clf = SVC()

    # # fit the model
    # svc_clf.fit(X_train, y_train)
    # clf_list.append(svc_clf)

    # print_metrics(svc_clf, X_test, y_test)

    # ## Neural Network
    # nn_clf = MLPClassifier()

    # # fit the model
    # nn_clf.fit(X_train, y_train)
    # clf_list.append(nn_clf)

    # print_metrics(nn_clf, X_test, y_test)

    # ## K-Neighbours Classifier
    knn_clf = KNeighborsClassifier()

    # fit the model
    knn_clf.fit(X_train, y_train)
    clf_list.append(knn_clf)

    print_metrics(knn_clf, X_test, y_test)

    # ## Decision Trees
    dt_clf = DecisionTreeClassifier()

    # fit the model
    dt_clf.fit(X_train, y_train)
    clf_list.append(dt_clf)

    print_metrics(dt_clf, X_test, y_test)

    # ## Random Forest
    # use different number of trees in forest
    forest_size = [10, 50, 100, 250]

    # set seed for random state to get compareable results in every execution (forest randomness)
    np.random.seed(500)

    for trees in forest_size:
        # set forest size
        print("Predicting with forest size " + str(trees))
        rf = RandomForestClassifier(n_estimators=trees)

        # fit the model
        rf.fit(X_train, y_train)
        clf_list.append(rf)

        print_metrics(rf, X_test, y_test)
        print("--------\n")

    # # Model Evaluation

    # ## Metrics + Confusion Matrices
    # generate list of plots for each clf: metrics, cf_matrix, cf_matrix_norm
    p_list = generate_model_plots(X_test, y_test, clf_list)

    # ## Save/display plots
    # params
    save_plots = True
    n_cols = 3
    document_title = "Music Features (1-3), all songs"
    document_folder = "music"  # lyrics, model, artist, all

    # save/display plots as jpg
    plots_from_list(
        document_title, p_list, document_folder, cols=n_cols, save=save_plots
    )

    # ## Confusion Matrix for Single Classifier
    # assign single classifier
    # cf_clf = None
    # normalized = "true"  # "true", "all" or None

    # # Confusion matrix
    # fig, cax = plt.subplots(figsize=(16, 16))  # subplot for larger size
    # cax.set_title(str(cf_clf), fontsize=15)
    # plot_confusion_matrix(
    #     estimator=cf_clf,
    #     X=X_test,
    #     y_true=y_test,
    #     cmap=plt.cm.Blues,
    #     normalize=normalized,
    #     values_format=".2f",
    #     ax=cax,
    # )

    # plt.show()

    # ## Scatter Plot
    # Params
    # sct_title = "Title"
    # sct_x = None
    # sct_xlabel = "x-label"
    # sct_y = None
    # sct_ylabel = "y-label"

    # # show scatter plot
    # plt.title(sct_title)
    # plt.xlabel(sct_x)
    # plt.ylabel(sct_y)
    # plt.scatter(sct_x, sct_y, s=5, alpha=0.5)
    # plt.show()

    # # add scatter plot to plot list
    # p_list.append(
    #     (
    #         plt.scatter,
    #         {"x": sct_x, "y": sct_y, "s": 5, "alpha": 0.5},
    #         sct_title,
    #         sct_xlabel,
    #         sct_ylabel,
    #     )
    # )

    # ## Bar Plot
    # # Params
    # bar_title = "Title"
    # bar_x = None
    # bar_xlabel = "x-label"
    # bar_height = None
    # bar_ylabel = "y-label"

    # # show bar plot
    # plt.title(sct_title)
    # plt.xlabel(sct_x)
    # plt.ylabel(sct_y)
    # plt.bar(sct_x, sct_y)
    # plt.show()

    # # add bar plot to plot list
    # p_list.append(
    #     (plt.bar, {"x": bar_x, "height": bar_height}, bar_title, bar_xlabel, bar_ylabel)
    # )

    # import src.training.postprocessing as pp

    # dummy = [x, y, "popularity", "song_count", "Plot Name"]

    # m = pp.get_metrics(knn_clf, X_test, y_test)

    # plist = [].append((plt.scatter, {"x": x,"y": y,"s": 5, "alpha": 0.5}, "xlabel", "ylabel", "p_name"))

    # y_lst = list(map(lambda x: len(x[1]),pd.DataFrame(y_test).groupby(0, as_index=True)))

    # plist.append((plt.bar, {"x": list(range(0,10)),"height": y_lst}, "Dataset Music V1 + unpredicted popularity", "popularity", "song count"))

    # plots_from_list(m, plist, "music", "test_plots_from_list_16")
