from utils import init_keyness_ranker
import os


def main():
    path_to_direc_corpora = os.path.join("exampleCorpora")
    subcorpora_sc = ("subcorpus1",)
    subcorpora_rc = ("subcorpus2", "subcorpus3")

    init_keyness_ranker(
        path_to_direc_corpora,
        subcorpora_sc,
        subcorpora_rc
    )


if __name__ == "__main__":
    main()
