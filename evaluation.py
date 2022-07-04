import jsonlines
from sklearn.metrics import accuracy_score, precision_score, confusion_matrix

DEFAULT_JSONL_DB = "nogit/finalOutput.jsonl"


def main():
    expected_data = load_expected_data(DEFAULT_JSONL_DB)
    predicted_data = load_predicted_data(DEFAULT_JSONL_DB)
    print_evaluation(expected_data, predicted_data)


def print_evaluation(y_true: list, y_pred: list):
    """
    Compare the two arguments and determine if the classification performed by the API was correct.

    :param y_true: The correct classification of the email message.
    :param y_pred: Classification of the message by the API.
    :return: print of the evaluation.
    """
    print("Accuracy")
    print(accuracy_score(y_true, y_pred))
    print("Accuracy not Normalized")
    print(accuracy_score(y_true, y_pred, normalize=False))
    print("Precision")
    print(precision_score(y_true, y_pred, average=None))
    print("Confusion Matrix")
    print(confusion_matrix(y_true, y_pred))


def load_expected_data(path_to_file):
    """
    Crate a list of the expected outputs
    :param path_to_file:
    :return: expected_result_list
    """
    expected_result_list = []
    with jsonlines.open(path_to_file, mode='r') as reader:
        for obj in reader.iter(type=dict, skip_invalid=True):
            expected_result = obj["phishing"]
            expected_result_list.append(expected_result)
    return expected_result_list


def load_predicted_data(path_to_file):
    """
    Crate a list of the outputs that the API returned
    :param path_to_file:
    :return: api_result_list
    """
    api_result_list = []
    with jsonlines.open(path_to_file, mode='r') as reader:
        for obj in reader.iter(type=dict, skip_invalid=True):
            api_result = obj["api_result"]
            api_result_list.append(api_result)
    return api_result_list


if __name__ == '__main__':
    main()
