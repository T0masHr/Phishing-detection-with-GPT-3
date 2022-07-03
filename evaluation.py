#  pip install -U scikit-learn
from sklearn.metrics import *

y_pred = [0, 0, 1, 0]  # Values that the model returns
y_true = [1, 0, 1, 0]  # Values we know that are correct


def accuracy(y_true: list, y_pred: list):
    accuracy_calculated = accuracy_score(y_true, y_pred)  # calculates accuracy
    return accuracy_calculated


def accuracy_normalized(y_true: list, y_pred: list):
    accuracy_calculated_normalized = accuracy_score(y_true, y_pred,
                                                    normalize=False)  # calculate the percentage of records correctly classified
    return accuracy_calculated_normalized


def precision(y_true: list, y_pred: list):
    precisions_calcualted = precision_score(y_true, y_pred, average=None)
    return precisions_calcualted


def confusion_matrix(y_true: list, y_pred: list):
    con_matrix = confusion_matrix(y_true, y_pred)
    return con_matrix


print(accuracy(y_true, y_pred))
print(accuracy_normalized(y_true, y_pred))
print(precision_score(y_true, y_pred, ))
print(confusion_matrix(y_true, y_pred))
