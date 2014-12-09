import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn import cross_validation
from sklearn.svm import SVR
from sklearn import preprocessing

# Input: list of features and a list of the same length of the actual distance
# Output: numpy 2D array (design matrix), numpy 1D array of the output variable
def create_design_matrix_and_labels(nlp_features, actual_shortest_path):
    assert len(nlp_features) == len(actual_shortest_path)

    design_matrix = []
    output_vector = []

    for i in range(len(nlp_features)):
        (name1, name2, feats) = nlp_features[i]
        (name1, name2, curr_path_len) = actual_shortest_path[i]

        design_matrix.append(feats)
        output_vector.append(curr_path_len)

    return (preprocessing.scale(np.array(design_matrix)), np.array(output_vector))

def split_test_dev_train(X, y, test_size, dev_size):
    X_test = X[0:test_size, :]
    y_test = y[0:test_size]
    X_dev = X[test_size:test_size+dev_size, :]
    y_dev = y[test_size:test_size+dev_size]
    X_train = X[test_size+dev_size:, :]
    y_train = y[test_size+dev_size:]
    return X_test, y_test, X_dev, y_dev, X_train, y_train
    

def run_ml(nlp_features, actual_shortest_path, is_dev=True):
    (design_matrix, output_labels) = create_design_matrix_and_labels(nlp_features, \
        actual_shortest_path)
    
    #X, X_test, y, y_test = cross_validation,train_test_split(design_matrix, output_labels, test_size=5000, random_state=0)
    #X_train, X_dev, y_train, y_dev = cross_validation,train_test_split(X, y, test_size=5000, random_state=0)

    frac = int(0.15 * len(nlp_features))
    X_test, y_test, X_dev, y_dev, X_train, y_train = split_test_dev_train(design_matrix, output_labels, frac, frac)

    model = LinearRegression().fit(X_train, y_train)
    #model = SVR().fit(X_train, y_train)

    score_test_or_dev = None
    score_train = None

    if is_dev:
        score_test_or_dev = model.score(X_dev, y_dev)
    else:
        score_test_or_dev = model.score(X_test, y_test)

    score_train = model.score(X_train, y_train)

    return (score_test_or_dev, score_train)