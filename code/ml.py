import numpy as np

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

    return (np.array(design_matrix), np.array(output_vector))


def run_ml(nlp_features, actual_shortest_path):
    (design_matrix, output_labels) = create_design_matrix_and_labels(nlp_features, \
        actual_shortest_path)

    # TODO






