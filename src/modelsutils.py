import pandas as pd
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score


def metrics(y_pred, y_true):
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary')
    return precision, recall, f1


def evaluate(x, y_true, predict):
    print('====== Evaluation summary ======')
    y_pred = predict(x)
    precision, recall, f1 = metrics(y_pred, y_true)
    auc = roc_auc_score(y_true, y_pred)
    print('Precision: {:.3f}'.format(precision))
    print('Recall: {:.3f}'.format(recall))
    print('F1-measure: {:.3f}'.format(f1))
    print('AUC: {:.3f}'.format(auc))
    return precision, recall, f1


def dropcol(df: pd.DataFrame, col: str) -> pd.DataFrame:
    return df.drop(col, axis=1)


def X(df: pd.DataFrame) -> pd.DataFrame:
    return dropcol(df, "defect_status")

def Y(df: pd.DataFrame) -> pd.DataFrame:
    return dropcol(df, "value")
