from keynessRanker_example_defs import init_keyness_ranker
import numpy as np
import os
import random
import sys


seed = 42
np.random.seed(seed)
random.seed(seed)


def main():
    path_to_direc_sc = os.path.join("exampleCorpora", "UD_Spanish-GSD")
    path_to_direc_rc = os.path.join("exampleCorpora", "UD_Spanish-AnCora")

    init_keyness_ranker(
        path_to_direc_sc,
        path_to_direc_rc
    )


if __name__ == "__main__":
    main()
