from .counters import multiple_250
from .process_JSONs import dump_json
import copy
import csv
import os
import random
import sys
from typing import Dict, List, Tuple


def d_freq(
        corpus_name: str,
        input_type: str,
        d_input: Dict,
        encoding_3_col_del: str,
        mapping_custom_to_ud: Dict,
        mapping_ud_to_custom: Dict,
        desired_pos: Tuple,
        lem_or_tok: str,
        maintain_subcorpora: bool,
        div_n_docs_by: int,
        n_iters: int
) -> Tuple[Dict, List]:
    """Construct frequency dictionaries (per item).
    :param corpus_name: name of the corpus.
    :param input_type: data type of the corpus documents.
    :param d_input: provided input data for the corpus.
    :param encoding_3_col_del: encoding of the corpus documents (when provided in 3-column format).
    :param mapping_custom_to_ud: if you work with custom POS tags, dictionary which maps custom tags to UD counterparts.
    :param mapping_ud_to_custom: if you work with custom POS tags, dictionary which maps UD tags to custom counterparts.
    :param desired_pos: tuple of UD tags which should be taken into account in the keyness calculations.
    :param lem_or_tok: defines whether to calculate frequencies on token or lemma level.
    :param maintain_subcorpora: when working with adjusted frequencies, boolean value which defines whether dispersion
        is based on existing subcorpora, or whether all documents are merged and randomly split into new subcorpora.
    :param div_n_docs_by: when working with adjusted frequencies, number by which the total number of documents is
        divided to arrive at the number of new randomly generated subcorpora.
    :param n_iters: when working with adjusted frequencies, number of times the subcorpora are randomly shuffled to
        generate new subcorpora (and, thus, also new dispersion values). This will lead to (slightly) different keyness
        values (and rankings), which are averaged out in the end.
    :return: a tuple containing a frequency dictionary of the entire corpus and a list of frequency dictionaries per
        corpus part.
    """
    l_pos = []

    for pos in desired_pos:

        for tag in mapping_ud_to_custom[pos]:
            l_pos.append(tag)

    # d_freq corpus and subcorpora
    if input_type == "3-column_delimited":
        d_tuples_corpus = {}
        l_docs_all = []

        for subcorpus in d_input:
            print(f"Number of files in {subcorpus}: {len(os.listdir(os.path.join(d_input[subcorpus])))}.")
            l_tuples_subcorpus = []
            id_doc = 0
            counter = 0

            for doc in os.listdir(os.path.join(d_input[subcorpus])):
                id_doc += 1
                docname = f"{subcorpus}_{id_doc}"
                l_docs_all.append(docname)

                if doc.endswith(".csv"):
                    delim = ","
                elif doc.endswith(".tsv"):
                    delim = "\t"
                else:
                    raise ValueError("Delimiter is not recognised.")

                with open(
                        os.path.join(d_input[subcorpus], doc), mode="r", encoding=encoding_3_col_del
                ) as f_delimited:
                    reader = csv.reader(f_delimited, delimiter=delim)

                    for row in reader:
                        tok = row[0]
                        pos = row[1]
                        lem = row[2]

                        if lem_or_tok == "lemma":

                            if pos in l_pos:

                                if maintain_subcorpora:
                                    l_tuples_subcorpus.append((lem, mapping_custom_to_ud[pos]))
                                else:
                                    l_tuples_subcorpus.append((lem, mapping_custom_to_ud[pos], docname))

                        elif lem_or_tok == "token":

                            if pos in l_pos:

                                if maintain_subcorpora:
                                    l_tuples_subcorpus.append((tok, mapping_custom_to_ud[pos]))
                                else:
                                    l_tuples_subcorpus.append((tok, mapping_custom_to_ud[pos], docname))

                        else:
                            raise ValueError("`lemma_or_token` is not correctly defined.")

                f_delimited.close()

                counter += 1
                multiple_250(counter)

            d_tuples_corpus[subcorpus] = l_tuples_subcorpus

    else:
        raise ValueError("`input_type` is not correctly defined.")

    d_freq_corpus = {"subcorpora": {}}
    d_freq_corpus_json = {"subcorpora": {}}
    d_freq_all = {}

    for subcorpus in d_tuples_corpus:
        d_freq_subcorpus = {}

        for tup in d_tuples_corpus[subcorpus]:
            tup_d_freq = (tup[0], tup[1])

            if tup_d_freq not in d_freq_subcorpus:
                d_freq_subcorpus[tup_d_freq] = 1
            else:
                d_freq_subcorpus[tup_d_freq] += 1

            if tup_d_freq not in d_freq_all:
                d_freq_all[tup_d_freq] = 1
            else:
                d_freq_all[tup_d_freq] += 1

        d_freq_subcorpus_json = {}

        for tup in d_freq_subcorpus:
            d_freq_subcorpus_json[str(tup)] = d_freq_subcorpus[tup]

        d_freq_corpus["subcorpora"][subcorpus] = d_freq_subcorpus
        d_freq_corpus_json["subcorpora"][subcorpus] = d_freq_subcorpus_json

    d_freq_all_json = {}

    for tup in d_freq_all:
        d_freq_all_json[str(tup)] = d_freq_all[tup]

    d_freq_corpus["corpus"] = d_freq_all
    d_freq_corpus_json["corpus"] = d_freq_all_json

    fn_d_freq = f"{corpus_name}_d_freq.json"
    dump_json(os.path.join("prep", corpus_name), fn_d_freq, d_freq_corpus_json)

    # d_freq corpus parts
    l_docs = list(dict.fromkeys(l_docs_all))
    l_d_freq_corpus_parts = []

    if maintain_subcorpora:
        d_freq_corpus_parts_iter = {}

        for subcorpus in d_freq_corpus["subcorpora"]:

            for tup in d_freq_corpus["subcorpora"][subcorpus]:
                item = tup[0]
                pos = tup[1]
                new_tup = (item, pos, subcorpus)
                d_freq_corpus_parts_iter[new_tup] = d_freq_corpus["subcorpora"][subcorpus][tup]

        for iteration in range(n_iters):
            l_d_freq_corpus_parts.append([{}, d_freq_corpus_parts_iter])

    else:
        l_d_cps = []
        n_docs = len(l_docs)
        n_cps = int(round(n_docs / div_n_docs_by))

        if n_cps < n_docs and n_cps != 0:
            assert 0 < n_cps <= n_docs

            for iteration in range(n_iters):
                d_cps_iter = {}
                l_docs_shuffled = copy.deepcopy(l_docs)
                random.shuffle(l_docs_shuffled)
                quot, remain = divmod(n_docs, n_cps)
                size_large = quot + 1
                l_docs_div = (
                        [l_docs_shuffled[part:part + size_large] for part in range(0, remain * size_large, size_large)]
                        + [l_docs_shuffled[part:part + quot] for part in range(remain * size_large, n_docs, quot)]
                )

                id_cp = 1

                for part in l_docs_div:
                    cp_name = f"corpus_part_{id_cp}"
                    d_cps_iter[cp_name] = part
                    id_cp += 1

                l_d_cps.append(d_cps_iter)

        else:
            d_cps_iter = {}
            id_cp = 1

            for part in l_docs:
                cp_name = f"corpus_part_{id_cp}"
                d_cps_iter[cp_name] = [part]
                id_cp += 1

            for iteration in range(n_iters):
                l_d_cps.append(d_cps_iter)

        for dic in l_d_cps:
            d_freq_corpus_parts_iter = {}
            d_cps_map = {}

            for cp in dic:

                for doc in dic[cp]:
                    d_cps_map[doc] = cp

            for subcorpus in d_tuples_corpus:

                for tup in d_tuples_corpus[subcorpus]:
                    item = tup[0]
                    pos = tup[1]
                    docname = tup[2]
                    cp = d_cps_map[docname]
                    new_tup = (item, pos, cp)

                    if new_tup not in d_freq_corpus_parts_iter:
                        d_freq_corpus_parts_iter[new_tup] = 1
                    else:
                        d_freq_corpus_parts_iter[new_tup] += 1

            l_d_freq_corpus_parts.append([dic, d_freq_corpus_parts_iter])

    return d_freq_corpus, l_d_freq_corpus_parts


def sum_words_desired_pos(
        corpus_name: str, d_freq_corpus: Dict, desired_pos: Tuple, l_d_freq_cps: List, maintain_subcorpora: bool,
        n_iters: int
) -> List:
    """Construct frequency dictionary (totals).
    :param corpus_name: name of the corpus.
    :param d_freq_corpus: frequency dictionary of the entire corpus.
    :param desired_pos: tuple of UD tags which should be taken into account in the keyness calculations.
    :param l_d_freq_cps: list of frequency dictionaries per corpus part.
    :param maintain_subcorpora: when working with adjusted frequencies, boolean value which defines whether dispersion
        is based on existing subcorpora, or whether all documents are merged and randomly split into new subcorpora.
    :param n_iters: when working with adjusted frequencies, number of times the subcorpora are randomly shuffled to
        generate new subcorpora (and, thus, also new dispersion values). This will lead to (slightly) different keyness
        values (and rankings), which are averaged out in the end.
    :return: list of dictionaries containing the sum of the words per corpus part.
    """

    # sum corpus
    d_sum_corpus = {"corpus": {"all": {"total": 0, "unique": 0}}, "subcorpora": {}}

    for subcorpus in d_freq_corpus["subcorpora"]:
        d_sum_corpus["subcorpora"][subcorpus] = {"all": {"total": 0, "unique": 0}}

    for pos in desired_pos:
        d_sum_corpus["corpus"][pos] = {"total": 0, "unique": 0}

        for subcorpus in d_freq_corpus["subcorpora"]:
            d_sum_corpus["subcorpora"][subcorpus][pos] = {"total": 0, "unique": 0}

    for tup in d_freq_corpus["corpus"]:
        pos = tup[1]
        d_sum_corpus["corpus"]["all"]["total"] += d_freq_corpus["corpus"][tup]
        d_sum_corpus["corpus"]["all"]["unique"] += 1
        d_sum_corpus["corpus"][pos]["total"] += d_freq_corpus["corpus"][tup]
        d_sum_corpus["corpus"][pos]["unique"] += 1

    for subcorpus in d_freq_corpus["subcorpora"]:

        for tup in d_freq_corpus["subcorpora"][subcorpus]:
            pos = tup[1]
            d_sum_corpus["subcorpora"][subcorpus]["all"]["total"] += d_freq_corpus["subcorpora"][subcorpus][tup]
            d_sum_corpus["subcorpora"][subcorpus]["all"]["unique"] += 1
            d_sum_corpus["subcorpora"][subcorpus][pos]["total"] += d_freq_corpus["subcorpora"][subcorpus][tup]
            d_sum_corpus["subcorpora"][subcorpus][pos]["unique"] += 1

    fn_d_sum_corpus = f"{corpus_name}_sum_words_desired_pos.json"
    dump_json(os.path.join("prep", corpus_name), fn_d_sum_corpus, d_sum_corpus)

    # sum corpus parts
    l_d_freq_sum_cps = []

    if maintain_subcorpora:
        d_sum_cps = {}

        for subcorpus in d_sum_corpus["subcorpora"]:
            d_sum_cps[subcorpus] = {}

        for subcorpus in d_sum_corpus["subcorpora"]:
            d_sum_cps[subcorpus]["total_all"] = d_sum_corpus["subcorpora"][subcorpus]["all"]["total"]
            d_sum_cps[subcorpus]["normalised_total_all"] = \
                d_sum_corpus["subcorpora"][subcorpus]["all"]["total"] / d_sum_corpus["corpus"]["all"]["total"]

            for pos in desired_pos:
                entry = f"total_{pos}"
                d_sum_cps[subcorpus][entry] = d_sum_corpus["subcorpora"][subcorpus][pos]["total"]

        for iteration in range(n_iters):
            d_freq_cps = l_d_freq_cps[iteration][1]
            l_d_freq_sum_cps.append([d_freq_cps, d_sum_cps])

    else:

        for item in l_d_freq_cps:
            d_cps = item[0]
            d_freq_cps = item[1]
            d_sum_cps = {}

            for part in d_cps:
                d_sum_cps[part] = {"total_all": 0}

                for pos in desired_pos:
                    entry = f"total_{pos}"
                    d_sum_cps[part][entry] = 0

            for tup in d_freq_cps:
                pos = tup[1]
                part = tup[2]
                d_sum_cps[part]["total_all"] += d_freq_cps[tup]
                d_sum_cps[part][f"total_{pos}"] += d_freq_cps[tup]

            for part in d_cps:
                d_sum_cps[part]["normalised_total_all"] =\
                    d_sum_cps[part]["total_all"] / d_sum_corpus["corpus"]["all"]["total"]

            l_d_freq_sum_cps.append([d_freq_cps, d_sum_cps])

    return l_d_freq_sum_cps


def corpora_to_d_freq(
        corpus_name: str,
        input_type: str,
        d_input: Dict,
        encoding_3_col_del: str,
        mapping_custom_to_ud: Dict,
        mapping_ud_to_custom: Dict,
        desired_pos: Tuple,
        lem_or_tok: str,
        maintain_subcorpora: bool,
        div_n_docs_by: int,
        n_iters: int
) -> Tuple[Dict, List]:
    """STEP_1: convert corpora into frequency dictionaries (data stored per corpus in "prep" folder).
    :param corpus_name: name of the corpus
    :param input_type: data type of the corpus documents.
    :param d_input: provided input data for the corpus.
    :param encoding_3_col_del: encoding of the corpus documents (when provided in 3-column format).
    :param mapping_custom_to_ud: if you work with custom POS tags, dictionary which maps custom tags to UD counterparts.
    :param mapping_ud_to_custom: if you work with custom POS tags, dictionary which maps UD tags to custom counterparts.
    :param desired_pos: tuple of UD tags which should be taken into account in the keyness calculations.
    :param lem_or_tok: defines whether to calculate frequencies on token or lemma level.
    :param maintain_subcorpora: when working with adjusted frequencies, boolean value which defines whether dispersion
        is based on existing subcorpora, or whether all documents are merged and randomly split into new subcorpora.
    :param div_n_docs_by: when working with adjusted frequencies, number by which the total number of documents is
        divided to arrive at the number of new randomly generated subcorpora.
    :param n_iters: when working with adjusted frequencies, number of times the subcorpora are randomly shuffled to
        generate new subcorpora (and, thus, also new dispersion values). This will lead to (slightly) different keyness
        values (and rankings), which are averaged out in the end.
    :return: a tuple containing a frequency dictionary of the entire corpus and a list of dictionaries containing the
    sum of the words per corpus part.
    """
    d_freq_corpus, l_d_freq_cps, = d_freq(
        corpus_name, input_type, d_input, encoding_3_col_del, mapping_custom_to_ud, mapping_ud_to_custom, desired_pos,
        lem_or_tok, maintain_subcorpora, div_n_docs_by, n_iters
    )
    l_d_freq_sum_cps = sum_words_desired_pos(
        corpus_name, d_freq_corpus, desired_pos, l_d_freq_cps, maintain_subcorpora, n_iters
    )

    return d_freq_corpus, l_d_freq_sum_cps
