from .process_JSONs import load_json
import os
import sys
from typing import Tuple


def check_meta(
        corpus_name: str, desired_pos: Tuple, lem_or_tok: str, maintain_subcorpora: bool, div_n_docs_by: int,
        n_iters: int
) -> bool:
    """Check if information in meta file corresponds to current query.
    :param corpus_name: name of the corpus.
    :param desired_pos: tuple of UD tags which should be taken into account in the keyness calculations.
    :param lem_or_tok: defines whether to calculate frequencies on token or lemma level.
    :param maintain_subcorpora: when working with adjusted frequencies, boolean value which defines whether dispersion
        is based on existing subcorpora, or whether all documents are merged and randomly split into new subcorpora.
    :param div_n_docs_by: when working with adjusted frequencies, number by which the total number of documents is
        divided to arrive at the number of new randomly generated subcorpora.
    :param n_iters: when working with adjusted frequencies, number of times the subcorpora are randomly shuffled to
        generate new subcorpora (and, thus, also new dispersion values). This will lead to (slightly) different keyness
        values (and rankings), which are averaged out in the end.
    :return: `True` if corresponds, `False` if not.
    """
    div_n_docs_by = div_n_docs_by if not maintain_subcorpora else None
    n_iters = n_iters if not maintain_subcorpora else None

    if os.path.exists(os.path.join("prep", corpus_name, f"{corpus_name}_meta.json")):
        d_meta_corpus = load_json(os.path.join("prep", corpus_name, f"{corpus_name}_meta.json"))

        if tuple(d_meta_corpus["desired_pos"]) == desired_pos \
                and d_meta_corpus["lemma_or_token"] == lem_or_tok \
                and d_meta_corpus["maintain_subcorpora"] == maintain_subcorpora \
                and d_meta_corpus["divide_number_docs_by"] == div_n_docs_by \
                and d_meta_corpus["number_iterations_merge_subcorpora"] == n_iters:
            return True
        else:
            return False

    else:
        return False
