from keynessRanker_example_defs import init_keyness_ranker
import numpy as np
import os
import random


seed = 42
np.random.seed(seed)
random.seed(seed)


def main():
    # define support variables
    path_to_direc_corpora = os.path.join("exampleCorpora")
    name_sc = "UD_Spanish-GSD"
    name_rc = "UD_Spanish-AnCora"

    # define variables to be passed into function
    d_sc = {
        "name": name_sc,
        "subcorpora": [os.path.join(path_to_direc_corpora, name_sc, "GSD_subcorpus1"),
                       os.path.join(path_to_direc_corpora, name_sc, "GSD_subcorpus2")]
    }
    d_rc = {
        "name": name_rc,
        "subcorpora": [os.path.join(path_to_direc_corpora, name_rc, "AnCora_subcorpus1"),
                       os.path.join(path_to_direc_corpora, name_rc, "AnCora_subcorpus3")]
    }

    # call function
    init_keyness_ranker(
        d_sc,
        d_rc
    )


if __name__ == "__main__":
    main()
