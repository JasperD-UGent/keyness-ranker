from defs.utils_defs import check_meta
from defs.utils_defs import load_json_sub1, load_json_sub1_str_to_obj
from defs.utils_defs import corpora_to_d_freq, dispersion, keyness, meta
from defs.utils_defs import results_to_xlsx_per_sc, results_to_xlsx_overview
from typing import Dict, Optional, Tuple
from collections import OrderedDict
import os


def init_keyness_ranker(
        path_to_direc_corpora: str,
        subcorpora_sc: Tuple,
        subcorpora_rc: Tuple,
        *,
        input_type_sc: str = "3-column_delimited",
        input_type_rc: str = "3-column_delimited",
        maintain_subcorpora_sc: bool = True,
        maintain_subcorpora_rc: bool = True,
        mapping_custom_to_ud: Optional[Dict] = None,
        mapping_ud_to_custom: Optional[Dict] = None,
        desired_pos: Tuple = ("NOUN", "ADJ", "VERB", "ADV"),
        lemma_or_token: str = "lemma",
        divide_number_docs_by: int = 10,
        number_iterations_merge_subcorpora: int = 1,
        approximation: float = 0.000000000000000001,
        statistical_significance_threshold_bic: int = 2,
        degrees_of_freedom: int = 1,
        frequency_type: str = "adj_freq_Lapl",
        keyness_metric: str = "LogRatio",
        ranking_threshold: float = 0.5,
):
    mapping_custom_to_ud = {"ADJ": "ADJ", "ADV": "ADV", "INTJ": "INTJ", "NOUN": "NOUN", "PROPN": "PROPN",
                            "VERB": "VERB", "ADP": "ADP", "AUX": "AUX", "CCONJ": "CCONJ", "DET": "DET", "NUM": "NUM",
                            "PART": "PART", "PRON": "PRON", "SCONJ": "SCONJ", "PUNCT": "PUNCT", "SYM": "SYM", "X": "X"} \
        if mapping_custom_to_ud is None else mapping_custom_to_ud
    mapping_ud_to_custom = {"ADJ": ["ADJ"], "ADV": ["ADV"], "INTJ": ["INTJ"], "NOUN": ["NOUN"], "PROPN": ["PROPN"],
                            "VERB": ["VERB"], "ADP": ["ADP"], "AUX": ["AUX"], "CCONJ": ["CCONJ"], "DET": ["DET"],
                            "NUM": ["NUM"], "PART": ["PART"], "PRON": ["PRON"], "SCONJ": ["SCONJ"], "PUNCT": ["PUNCT"],
                            "SYM": ["SYM"], "X": ["X"]} \
        if mapping_ud_to_custom is None else mapping_ud_to_custom
    number_iterations_merge_subcorpora = 1 if maintain_subcorpora_sc and maintain_subcorpora_rc\
        else number_iterations_merge_subcorpora

    d_keyn_overview = OrderedDict()

    if len(subcorpora_sc) > 1:
        d_keyn_per_rc = OrderedDict()
        name_sc = "_".join(subcorpora_sc)
        input_sc = {}

        for corpus in subcorpora_sc:
            input_sc[corpus] = os.path.join(path_to_direc_corpora, corpus)

        load_from_files_sc = check_meta(
            name_sc, maintain_subcorpora_sc, desired_pos, lemma_or_token, divide_number_docs_by,
            number_iterations_merge_subcorpora)

        if load_from_files_sc:
            d_freq_abs_adj_sc = load_json_sub1_str_to_obj("prep", name_sc, "_d_freq_abs_adj")
            l_d_sum_abs_adj_sc = load_json_sub1("prep", name_sc, "_sum_words_desired_POS_abs_adj")

        else:
            d_freq_sc, l_d_freq_sum_cps_sc = corpora_to_d_freq(
                name_sc, input_type_sc, input_sc, maintain_subcorpora_sc, mapping_custom_to_ud,
                mapping_ud_to_custom, desired_pos, lemma_or_token, divide_number_docs_by,
                number_iterations_merge_subcorpora)
            meta(name_sc, maintain_subcorpora_sc, desired_pos, lemma_or_token, divide_number_docs_by,
                 number_iterations_merge_subcorpora)
            d_freq_abs_adj_sc, l_d_sum_abs_adj_sc = dispersion(
                name_sc, desired_pos, d_freq_sc, l_d_freq_sum_cps_sc, number_iterations_merge_subcorpora)

        if len(subcorpora_rc) > 1:
            name_rc = "_".join(subcorpora_rc)
            input_rc = {}

            for corpus in subcorpora_rc:
                input_rc[corpus] = os.path.join(path_to_direc_corpora, corpus)

            load_from_files_rc = check_meta(
                name_rc, maintain_subcorpora_rc, desired_pos, lemma_or_token, divide_number_docs_by,
                number_iterations_merge_subcorpora)

            if load_from_files_rc:
                d_freq_abs_adj_rc = load_json_sub1_str_to_obj("prep", name_rc, "_d_freq_abs_adj")
                l_d_sum_abs_adj_rc = load_json_sub1("prep", name_rc, "_sum_words_desired_POS_abs_adj")

            else:
                d_freq_rc, l_d_freq_sum_cps_rc = corpora_to_d_freq(
                    name_rc, input_type_rc, input_rc, maintain_subcorpora_rc, mapping_custom_to_ud,
                    mapping_ud_to_custom, desired_pos, lemma_or_token, divide_number_docs_by,
                    number_iterations_merge_subcorpora)
                meta(name_rc, maintain_subcorpora_rc, desired_pos, lemma_or_token, divide_number_docs_by,
                     number_iterations_merge_subcorpora)
                d_freq_abs_adj_rc, l_d_sum_abs_adj_rc = dispersion(
                    name_rc, desired_pos, d_freq_rc, l_d_freq_sum_cps_rc, number_iterations_merge_subcorpora)

            l_d_keyn_corpus = keyness(
                number_iterations_merge_subcorpora, approximation, statistical_significance_threshold_bic,
                degrees_of_freedom, frequency_type, keyness_metric, d_freq_abs_adj_sc, l_d_sum_abs_adj_sc,
                d_freq_abs_adj_rc, l_d_sum_abs_adj_rc)

            d_keyn_per_rc[name_rc] = l_d_keyn_corpus

        for corpus in subcorpora_rc:
            name_rc = corpus
            input_rc = {corpus: os.path.join(path_to_direc_corpora, corpus)}

            load_from_files_rc = check_meta(
                name_rc, maintain_subcorpora_rc, desired_pos, lemma_or_token, divide_number_docs_by,
                number_iterations_merge_subcorpora)

            if load_from_files_rc:
                d_freq_abs_adj_rc = load_json_sub1_str_to_obj("prep", name_rc, "_d_freq_abs_adj")
                l_d_sum_abs_adj_rc = load_json_sub1("prep", name_rc, "_sum_words_desired_POS_abs_adj")

            else:
                d_freq_rc, l_d_freq_sum_cps_rc = corpora_to_d_freq(
                    name_rc, input_type_rc, input_rc, maintain_subcorpora_rc, mapping_custom_to_ud,
                    mapping_ud_to_custom, desired_pos, lemma_or_token, divide_number_docs_by,
                    number_iterations_merge_subcorpora)
                meta(name_rc, maintain_subcorpora_rc, desired_pos, lemma_or_token, divide_number_docs_by,
                     number_iterations_merge_subcorpora)
                d_freq_abs_adj_rc, l_d_sum_abs_adj_rc = dispersion(
                    name_rc, desired_pos, d_freq_rc, l_d_freq_sum_cps_rc, number_iterations_merge_subcorpora)

            l_d_keyn_corpus = keyness(
                number_iterations_merge_subcorpora, approximation, statistical_significance_threshold_bic,
                degrees_of_freedom, frequency_type, keyness_metric, d_freq_abs_adj_sc, l_d_sum_abs_adj_sc,
                d_freq_abs_adj_rc, l_d_sum_abs_adj_rc)

            d_keyn_per_rc[name_rc] = l_d_keyn_corpus

        d_keyn_sc = OrderedDict()

        for corpus in d_keyn_per_rc:

            for iteration in range(number_iterations_merge_subcorpora):

                for tup in d_keyn_per_rc[corpus][iteration]:

                    if tup not in d_keyn_sc:
                        d_keyn_sc[tup] = {}

                        for reference_corpus in d_keyn_per_rc.keys():
                            d_keyn_sc[tup][reference_corpus] =\
                                ["NA" for iteration in range(number_iterations_merge_subcorpora)]

                    d_keyn_sc[tup][corpus][iteration] = d_keyn_per_rc[corpus][iteration][tup]

        l_d_keyn = []

        for tup in d_keyn_sc:
            d_keyn_iters = {}
            sum_ranking_scores = 0
            sum_keyn_scores = 0
            n_rankings = 0

            for corpus in d_keyn_sc[tup]:
                d_keyn_iters[corpus] = d_keyn_sc[tup][corpus]
                sum_ranking_scores_corpus = 0
                sum_keyn_scores_corpus = 0
                n_rankings_corpus = 0

                for item in d_keyn_sc[tup][corpus]:

                    if item == "NA":
                        pass
                    else:
                        sum_ranking_scores_corpus += item["ranking_score"]
                        sum_keyn_scores_corpus += item["keyn"]
                        n_rankings_corpus += 1

                if n_rankings_corpus == 0:
                    pass
                else:
                    sum_ranking_scores += sum_ranking_scores_corpus / n_rankings_corpus
                    sum_keyn_scores += sum_keyn_scores_corpus / n_rankings_corpus
                    n_rankings += 1

            l_d_keyn.append({"item": tup,
                             "d_keyn": d_keyn_iters,
                             "ranking_score_avg": sum_ranking_scores / n_rankings,
                             "keyness_score_avg": sum_keyn_scores / n_rankings,
                             "n_rankings": n_rankings})

        sorted_l_d_keyn = sorted(
            sorted(l_d_keyn, key=lambda i: i["item"]), key=lambda i: i["ranking_score_avg"], reverse=True)  # sort key items by 1) ranking_score_avg (descending); 2) pos_lem_or_tok (ascending)

        results_to_xlsx_per_sc(subcorpora_sc, subcorpora_rc, name_sc, lemma_or_token, keyness_metric,
                               frequency_type, ranking_threshold, sorted_l_d_keyn, d_keyn_per_rc,
                               maintain_subcorpora_sc, maintain_subcorpora_rc)

        d_keyn_overview[name_sc] = sorted_l_d_keyn

    for study_corpus in subcorpora_sc:
        name_sc = study_corpus
        d_keyn_per_rc = OrderedDict()
        input_sc = {study_corpus: os.path.join(path_to_direc_corpora, study_corpus)}

        load_from_files_sc = check_meta(
            name_sc, maintain_subcorpora_sc, desired_pos, lemma_or_token, divide_number_docs_by,
            number_iterations_merge_subcorpora)

        if load_from_files_sc:
            d_freq_abs_adj_sc = load_json_sub1_str_to_obj("prep", name_sc, "_d_freq_abs_adj")
            l_d_sum_abs_adj_sc = load_json_sub1("prep", name_sc, "_sum_words_desired_POS_abs_adj")

        else:
            d_freq_sc, l_d_freq_sum_cps_sc = corpora_to_d_freq(
                name_sc, input_type_sc, input_sc, maintain_subcorpora_sc, mapping_custom_to_ud,
                mapping_ud_to_custom, desired_pos, lemma_or_token, divide_number_docs_by,
                number_iterations_merge_subcorpora)
            meta(name_sc, maintain_subcorpora_sc, desired_pos, lemma_or_token, divide_number_docs_by,
                 number_iterations_merge_subcorpora)
            d_freq_abs_adj_sc, l_d_sum_abs_adj_sc = dispersion(
                name_sc, desired_pos, d_freq_sc, l_d_freq_sum_cps_sc, number_iterations_merge_subcorpora)

        if len(subcorpora_rc) > 1:
            name_rc = "_".join(subcorpora_rc)
            input_rc = {}

            for corpus in subcorpora_rc:
                input_rc[corpus] = os.path.join(path_to_direc_corpora, corpus)

            load_from_files_rc = check_meta(
                name_rc, maintain_subcorpora_rc, desired_pos, lemma_or_token, divide_number_docs_by,
                number_iterations_merge_subcorpora)

            if load_from_files_rc:
                d_freq_abs_adj_rc = load_json_sub1_str_to_obj("prep", name_rc, "_d_freq_abs_adj")
                l_d_sum_abs_adj_rc = load_json_sub1("prep", name_rc, "_sum_words_desired_POS_abs_adj")

            else:
                d_freq_rc, l_d_freq_sum_cps_rc = corpora_to_d_freq(
                    name_rc, input_type_rc, input_rc, maintain_subcorpora_rc, mapping_custom_to_ud,
                    mapping_ud_to_custom, desired_pos, lemma_or_token, divide_number_docs_by,
                    number_iterations_merge_subcorpora)
                meta(name_rc, maintain_subcorpora_rc, desired_pos, lemma_or_token, divide_number_docs_by,
                     number_iterations_merge_subcorpora)
                d_freq_abs_adj_rc, l_d_sum_abs_adj_rc = dispersion(
                    name_rc, desired_pos, d_freq_rc, l_d_freq_sum_cps_rc, number_iterations_merge_subcorpora)

            l_d_keyn_corpus = keyness(
                number_iterations_merge_subcorpora, approximation, statistical_significance_threshold_bic,
                degrees_of_freedom, frequency_type, keyness_metric, d_freq_abs_adj_sc, l_d_sum_abs_adj_sc,
                d_freq_abs_adj_rc, l_d_sum_abs_adj_rc)

            d_keyn_per_rc[name_rc] = l_d_keyn_corpus

        for corpus in subcorpora_rc:
            name_rc = corpus
            input_rc = {corpus: os.path.join(path_to_direc_corpora, corpus)}

            load_from_files_rc = check_meta(
                name_rc, maintain_subcorpora_rc, desired_pos, lemma_or_token, divide_number_docs_by,
                number_iterations_merge_subcorpora)

            if load_from_files_rc:
                d_freq_abs_adj_rc = load_json_sub1_str_to_obj("prep", name_rc, "_d_freq_abs_adj")
                l_d_sum_abs_adj_rc = load_json_sub1("prep", name_rc, "_sum_words_desired_POS_abs_adj")

            else:
                d_freq_rc, l_d_freq_sum_cps_rc = corpora_to_d_freq(
                    name_rc, input_type_rc, input_rc, maintain_subcorpora_rc, mapping_custom_to_ud,
                    mapping_ud_to_custom, desired_pos, lemma_or_token, divide_number_docs_by,
                    number_iterations_merge_subcorpora)
                meta(name_rc, maintain_subcorpora_rc, desired_pos, lemma_or_token, divide_number_docs_by,
                     number_iterations_merge_subcorpora)
                d_freq_abs_adj_rc, l_d_sum_abs_adj_rc = dispersion(
                    name_rc, desired_pos, d_freq_rc, l_d_freq_sum_cps_rc, number_iterations_merge_subcorpora)

            l_d_keyn_corpus = keyness(
                number_iterations_merge_subcorpora, approximation, statistical_significance_threshold_bic,
                degrees_of_freedom, frequency_type, keyness_metric, d_freq_abs_adj_sc, l_d_sum_abs_adj_sc,
                d_freq_abs_adj_rc, l_d_sum_abs_adj_rc)

            d_keyn_per_rc[name_rc] = l_d_keyn_corpus

        d_keyn_sc = OrderedDict()

        for corpus in d_keyn_per_rc:

            for iteration in range(number_iterations_merge_subcorpora):

                for tup in d_keyn_per_rc[corpus][iteration]:

                    if tup not in d_keyn_sc:
                        d_keyn_sc[tup] = {}

                        for reference_corpus in d_keyn_per_rc.keys():
                            d_keyn_sc[tup][reference_corpus] = \
                                ["NA" for iteration in range(number_iterations_merge_subcorpora)]

                    d_keyn_sc[tup][corpus][iteration] = d_keyn_per_rc[corpus][iteration][tup]

        l_d_keyn = []

        for tup in d_keyn_sc:
            d_keyn_iters = {}
            sum_ranking_scores = 0
            sum_keyn_scores = 0
            n_rankings = 0

            for corpus in d_keyn_sc[tup]:
                d_keyn_iters[corpus] = d_keyn_sc[tup][corpus]
                sum_ranking_scores_corpus = 0
                sum_keyn_scores_corpus = 0
                n_rankings_corpus = 0

                for item in d_keyn_sc[tup][corpus]:

                    if item == "NA":
                        pass
                    else:
                        sum_ranking_scores_corpus += item["ranking_score"]
                        sum_keyn_scores_corpus += item["keyn"]
                        n_rankings_corpus += 1

                if n_rankings_corpus == 0:
                    pass
                else:
                    sum_ranking_scores += sum_ranking_scores_corpus / n_rankings_corpus
                    sum_keyn_scores += sum_keyn_scores_corpus / n_rankings_corpus
                    n_rankings += 1

            l_d_keyn.append({"item": tup,
                             "d_keyn": d_keyn_iters,
                             "ranking_score_avg": sum_ranking_scores / n_rankings,
                             "keyness_score_avg": sum_keyn_scores / n_rankings,
                             "n_rankings": n_rankings})

        sorted_l_d_keyn = sorted(
            sorted(l_d_keyn, key=lambda i: i["item"]), key=lambda i: i["ranking_score_avg"], reverse=True)  # sort key items by 1) ranking_score_avg (descending); 2) pos_lem_or_tok (ascending)

        results_to_xlsx_per_sc(subcorpora_sc, subcorpora_rc, name_sc, lemma_or_token, keyness_metric,
                               frequency_type, ranking_threshold, sorted_l_d_keyn, d_keyn_per_rc,
                               maintain_subcorpora_sc, maintain_subcorpora_rc)

        d_keyn_overview[name_sc] = sorted_l_d_keyn

    d_keyn_all_scs = OrderedDict()

    for corpus in d_keyn_overview:

        for dic in d_keyn_overview[corpus]:
            tup = dic["item"]

            if tup not in d_keyn_all_scs:
                d_keyn_all_scs[tup] = {}

                for study_corpus in d_keyn_overview.keys():
                    d_keyn_all_scs[tup][study_corpus] = "NA"

            d_keyn_all_scs[tup][corpus] = dic

    l_d_keyn_all = []

    for tup in d_keyn_all_scs:
        sum_ranking_scores = 0
        sum_keyn_scores = 0
        n_rankings = 0

        for corpus in d_keyn_all_scs[tup]:

            if d_keyn_all_scs[tup][corpus] == "NA":
                pass
            else:
                sum_ranking_scores += d_keyn_all_scs[tup][corpus]["ranking_score_avg"]
                sum_keyn_scores += d_keyn_all_scs[tup][corpus]["keyness_score_avg"]
                n_rankings += 1

        l_d_keyn_all.append({"item": tup,
                             "d_keyn": d_keyn_all_scs[tup],
                             "ranking_score_avg_avg": sum_ranking_scores / n_rankings,
                             "keyness_score_avg_avg": sum_keyn_scores / n_rankings,
                             "n_rankings": n_rankings})

    sorted_l_d_keyn_all = sorted(
        sorted(l_d_keyn_all, key=lambda i: i["item"]), key=lambda i: i["ranking_score_avg_avg"], reverse=True)  # sort key items by 1) ranking_score_avg (descending); 2) pos_lem_or_tok (ascending)

    results_to_xlsx_overview(subcorpora_sc, subcorpora_rc, lemma_or_token, keyness_metric, frequency_type,
                             ranking_threshold, sorted_l_d_keyn_all, d_keyn_overview, maintain_subcorpora_sc,
                             maintain_subcorpora_rc)
