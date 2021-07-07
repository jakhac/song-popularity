import pickle
import os
from dotenv import load_dotenv
from pathlib import Path

from sklearn import model_selection
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

import matplotlib.pyplot as plt

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
    metrics += "Accuracy: " + str(round(accuracy_score(y_test, y_predict), 4)) + "\n"
    metrics += (
        "F1: " + str(round(f1_score(y_test, y_predict, average="weighted"), 4)) + "\n"
    )
    metrics += (
        "Recall: "
        + str(round(recall_score(y_test, y_predict, average="weighted"), 4))
        + "\n"
    )
    metrics += (
        "Precision: "
        + str(round(precision_score(y_test, y_predict, average="weighted"), 4))
        + "\n\n"
    )

    # check which labels do not appear in prediction
    metrics += f"Contained predictions: {set(y_predict)}" + "\n"
    metrics += f"Contained tests: {set(y_test)}" + "\n"

    return metrics
