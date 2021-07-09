import os
import pickle
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
from sklearn import model_selection
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

load_dotenv()
DATA_PATH = os.getenv("DATA_PATH")


def store_model_to_file(model, model_name: str, model_type: str):

    model_dir = Path(DATA_PATH) / "models" / model_type

    if not model_dir.is_dir():
        model_dir.mkdir(parents=True, exist_ok=True)

    pickle.dump(model, open(model_dir / (model_name + ".mdl"), "wb"))


def load_model(model_name: str, model_type: str):

    model_dir = Path(DATA_PATH) / "models" / model_type
    return pickle.load(open(model_dir / (model_name + ".mdl"), "rb"))


def get_metrics(clf, X_test, y_test):
    # predict on test set
    y_predict = clf.predict(X_test)
    metrics = ""

    # print metrics
    metrics += (
        "Weighted accuracy: " + str(round(accuracy_score(y_test, y_predict), 4)) + "\n"
    )
    metrics += (
        "Weighted f1: "
        + str(round(f1_score(y_test, y_predict, average="weighted"), 4))
        + "\n"
    )
    metrics += (
        "Weighted recall: "
        + str(round(recall_score(y_test, y_predict, average="weighted"), 4))
        + "\n"
    )
    metrics += (
        "Weighted precision: "
        + str(round(precision_score(y_test, y_predict, average="weighted"), 4))
        + "\n"
    )

    # check which labels do not appear in prediction
    metrics += f"Contained classes in prediction: {set(y_predict)}" + "\n"
    metrics += f"Contained classes in test: {set(y_test)}"
    return metrics


def print_metrics(clf, X_test, y_test):
    print(get_metrics(clf, X_test, y_test))


def count_distribution(data: List[int]) -> List[int]:
    return list(pd.DataFrame(data).value_counts(sort=False))
