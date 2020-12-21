import codecs
import os
import json
from ast import literal_eval
import csv
import copy
import random
import numpy as np
import xlsxwriter
import statistics

# counter that prints every multiple of 250


def multiple_250(counter):

    if (counter / 250).is_integer():
        print(counter)
    else:
        pass

# dump JSON file in folder at root level


def dump_json_root(direc, fn, variable):

    if not os.path.isdir(os.path.join(direc)):
        os.mkdir(os.path.join(direc))

    fn_complete = fn + ".json"

    with codecs.open(os.path.join(direc, fn_complete), "w", "utf-8-sig") as f:
        json.dump(variable, f, indent=2)
    f.close()


# dump JSON file in folder at root/subfolder level


def dump_json_sub1(root_direc, direc_sub1, fn, variable):

    if not os.path.isdir(os.path.join(root_direc)):
        os.mkdir(os.path.join(root_direc))

    if not os.path.isdir(os.path.join(root_direc, direc_sub1)):
        os.mkdir(os.path.join(root_direc, direc_sub1))

    fn_complete = fn + ".json"

    with codecs.open(os.path.join(root_direc, direc_sub1, fn_complete), "w", "utf-8-sig") as f:
        json.dump(variable, f, indent=2)
    f.close()

# check if information in meta file corresponds to current query


def check_meta(corpus_name, maintain_subcorpora, desired_pos, lem_or_tok, div_n_docs_by, n_iters):

    if os.path.exists(os.path.join("prep", corpus_name, corpus_name + "_meta.json")):

        with codecs.open(os.path.join("prep", corpus_name, corpus_name + "_meta.json"), "r", "utf-8-sig") as f_meta:
            d_meta_corpus = json.load(f_meta)
        f_meta.close()

        if d_meta_corpus["maintain_subcorpora"] == maintain_subcorpora\
                and tuple(d_meta_corpus["desired_POS"]) == desired_pos\
                and d_meta_corpus["lemma_or_token"] == lem_or_tok\
                and d_meta_corpus["divide_number_docs_by"] == div_n_docs_by\
                and d_meta_corpus["number_iterations_merge_subcorpora"] == n_iters:
            return True

        else:
            return False

    else:
        return False

# load JSON file at root/subfolder level


def load_json_sub1(direc, corpus_name, fn_ending):
    fn_complete = corpus_name + fn_ending + ".json"

    with codecs.open(os.path.join(direc, corpus_name, fn_complete), "r", "utf-8-sig") as f:
        f_loaded = json.load(f)
    f.close()

    print("finished loading", fn_complete)

    return f_loaded

# load JSON file at root/subfolder level and reconvert strings into objects


def load_json_sub1_str_to_obj(direc, corpus_name, fn_ending):
    fn_complete = corpus_name + fn_ending + ".json"

    with codecs.open(os.path.join(direc, corpus_name, fn_complete), "r", "utf-8-sig") as f:
        f_loaded = json.load(f)
    f.close()

    print("finished loading", fn_complete)

    f_loaded_new = {}

    for string in f_loaded:
        f_loaded_new[literal_eval(string)] = f_loaded[string]

    return f_loaded_new

# construct frequency dictionary (per item)


def d_freq(corpus_name, input_type, d_input, maintain_subcorpora, mapping_custom_to_ud, mapping_ud_to_custom,
           desired_pos, lem_or_tok, div_n_docs_by, n_iters):
    l_pos = []

    for pos in desired_pos:

        for tag in mapping_ud_to_custom[pos]:
            l_pos.append(tag)

    # d_freq corpus and subcorpora

    if input_type == "3-column_delimited":
        d_tuples_corpus = {}
        l_docs_all = []

        for subcorpus in d_input:
            print("number of files in", subcorpus, ":", len(os.listdir(os.path.join(d_input[subcorpus]))))
            l_tuples_subcorpus = []
            id_doc = 0
            counter = 0

            for doc in os.listdir(os.path.join(d_input[subcorpus])):
                id_doc += 1
                docname = subcorpus + "_" + str(id_doc)
                l_docs_all.append(docname)

                if doc.endswith(".csv"):
                    delim = ","
                    docname_orig = doc.replace(".csv", "")
                elif doc.endswith(".tsv"):
                    delim = "\t"
                    docname_orig = doc.replace(".tsv", "")
                else:
                    raise ValueError("Delimiter is not recognised.")

                with open(os.path.join(d_input[subcorpus], doc), mode="r") as f_delimited:
                    reader = csv.reader(f_delimited, delimiter=delim)

                    for row in reader:
                        tok = row[0]
                        pos = row[1]
                        lem = row[2]

                        if lem_or_tok == "lemma":

                            if pos in l_pos and lem not in ["<unknown>", "unknown"]:

                                if maintain_subcorpora:
                                    l_tuples_subcorpus.append(tuple([lem, mapping_custom_to_ud[pos]]))

                                else:
                                    l_tuples_subcorpus.append(tuple([lem, mapping_custom_to_ud[pos], docname]))

                        elif lem_or_tok == "token":

                            if pos in l_pos:

                                if maintain_subcorpora:
                                    l_tuples_subcorpus.append(tuple([tok, mapping_custom_to_ud[pos]]))

                                else:
                                    l_tuples_subcorpus.append(tuple([tok, mapping_custom_to_ud[pos], docname]))

                        else:
                            raise ValueError("lemma_or_token is not correctly defined.")

                f_delimited.close()

                counter += 1
                multiple_250(counter)

            d_tuples_corpus[subcorpus] = l_tuples_subcorpus

    else:
        raise ValueError("input_type is not correctly defined.")

    d_freq_corpus = {"subcorpora": {}}
    d_freq_corpus_json = {"subcorpora": {}}
    d_freq_all = {}

    for subcorpus in d_tuples_corpus:
        d_freq_subcorpus = {}

        for tup in d_tuples_corpus[subcorpus]:
            tup_d_freq = tuple((tup[0], tup[1]))

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

    fn_d_freq = corpus_name + "_d_freq"
    dump_json_sub1("prep", corpus_name, fn_d_freq, d_freq_corpus_json)

    # d_freq corpus parts

    l_docs = list(dict.fromkeys(l_docs_all))
    l_d_freq_corpus_parts = []

    if maintain_subcorpora:
        d_freq_corpus_parts_iter = {}

        for subcorpus in d_freq_corpus["subcorpora"]:

            for tup in d_freq_corpus["subcorpora"][subcorpus]:
                item = tup[0]
                pos = tup[1]
                new_tup = tuple([item, pos, subcorpus])
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
                            [l_docs_shuffled[part:part + size_large]
                             for part in range(0, remain * size_large, size_large)]
                            + [l_docs_shuffled[part:part + quot]
                               for part in range(remain * size_large, n_docs, quot)])

                id_cp = 1

                for part in l_docs_div:
                    cp_name = "corpus_part_" + str(id_cp)
                    d_cps_iter[cp_name] = part
                    id_cp += 1

                l_d_cps.append(d_cps_iter)

        else:
            d_cps_iter = {}
            id_cp = 1

            for part in l_docs:
                cp_name = "corpus_part_" + str(id_cp)
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
                    new_tup = tuple([item, pos, cp])

                    if new_tup not in d_freq_corpus_parts_iter:
                        d_freq_corpus_parts_iter[new_tup] = 1
                    else:
                        d_freq_corpus_parts_iter[new_tup] += 1

            l_d_freq_corpus_parts.append([dic, d_freq_corpus_parts_iter])

    return d_freq_corpus, l_d_freq_corpus_parts

# construct frequency dictionary (totals)


def sum_words_desired_pos(corpus_name, d_freq_corpus, maintain_subcorpora, desired_pos, n_iters, l_d_freq_cps):

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

    fn_d_sum_corpus = corpus_name + "_sum_words_desired_POS"
    dump_json_sub1("prep", corpus_name, fn_d_sum_corpus, d_sum_corpus)

    # sum corpus parts

    l_d_freq_sum_cps = []

    if maintain_subcorpora:
        d_sum_cps = {}

        for subcorpus in d_sum_corpus["subcorpora"]:
            d_sum_cps[subcorpus] = {}

        for subcorpus in d_sum_corpus["subcorpora"]:
            d_sum_cps[subcorpus]["total_all"] = d_sum_corpus["subcorpora"][subcorpus]["all"]["total"]
            d_sum_cps[subcorpus]["normalised_total_all"] =\
                d_sum_corpus["subcorpora"][subcorpus]["all"]["total"] / d_sum_corpus["corpus"]["all"]["total"]

            for pos in desired_pos:
                entry = "total_" + pos
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
                    entry = "total_" + pos
                    d_sum_cps[part][entry] = 0

            for tup in d_freq_cps:
                pos = tup[1]
                part = tup[2]
                d_sum_cps[part]["total_all"] += d_freq_cps[tup]
                d_sum_cps[part]["total_" + pos] += d_freq_cps[tup]

            for part in d_cps:
                d_sum_cps[part]["normalised_total_all"] =\
                    d_sum_cps[part]["total_all"] / d_sum_corpus["corpus"]["all"]["total"]

            l_d_freq_sum_cps.append([d_freq_cps, d_sum_cps])

    return l_d_freq_sum_cps

# construct meta file


def d_meta(corpus_name, maintain_subcorpora, desired_pos, lem_or_tok, div_n_docs_by, n_iters):
    d_meta_corpus = {"maintain_subcorpora": maintain_subcorpora,
                     "desired_POS": desired_pos,
                     "lemma_or_token": lem_or_tok,
                     "divide_number_docs_by": div_n_docs_by,
                     "number_iterations_merge_subcorpora": n_iters}

    dump_json_sub1("prep", corpus_name, corpus_name + "_meta", d_meta_corpus)

# calculate dispersion values (DPnorm)


def dp(corpus_name, d_freq_corpus, l_d_freq_sum_cps):
    d_dp_norm = {}

    for tup in d_freq_corpus["corpus"]:
        d_dp_norm[tup] = []

    for item in l_d_freq_sum_cps:
        d_freq_cps = item[0]
        d_sum_cps = item[1]

        if len(d_sum_cps) == 1:

            for tup in d_freq_corpus["corpus"]:
                d_dp_norm[tup].append(0)

        else:
            l_norm_sum_cps = [d_sum_cps[part]["normalised_total_all"] for part in d_sum_cps]
            smallest_cp = min(l_norm_sum_cps)

            d_dp = {}

            for part in d_sum_cps:

                for tup in d_freq_corpus["corpus"]:
                    expected = d_sum_cps[part]["normalised_total_all"]
                    entry = tuple([tup[0], tup[1], part])

                    if entry in d_freq_cps:
                        freq_part = d_freq_cps[entry]
                    else:
                        freq_part = 0

                    freq_corpus = d_freq_corpus["corpus"][tup]
                    observed = freq_part / freq_corpus
                    abs_diff = abs(expected - observed)

                    if tup not in d_dp:
                        d_dp[tup] = abs_diff * 0.5
                    else:
                        d_dp[tup] += abs_diff * 0.5

            for tup in d_dp:
                d_dp_norm[tup].append(d_dp[tup] / (1 - smallest_cp))

    d_dp_norm_json = {}

    for tup in d_dp_norm:
        d_dp_norm_json[str(tup)] = d_dp_norm[tup]

    fn_d_dp = corpus_name + "_DP"
    dump_json_sub1("prep", corpus_name, fn_d_dp, d_dp_norm_json)

    return d_dp_norm

# add adjusted frequencies to frequency dictionary (per item)


def d_freq_abs_adj(corpus_name, d_freq_corpus, d_dp):
    d_abs_adj = {}

    for tup in d_freq_corpus["corpus"]:
        d_tup = {
            "DP": [],
            "abs_freq": [],
            "adj_freq": [],
            "abs_freq_Lapl": [],
            "adj_freq_Lapl": []
        }

        for dp_score in d_dp[tup]:
            adj_freq = d_freq_corpus["corpus"][tup] * (1 - dp_score)
            abs_freq_lapl = d_freq_corpus["corpus"][tup] + 1
            adj_freq_lapl = (d_freq_corpus["corpus"][tup] * (1 - dp_score)) + 1

            d_tup["DP"].append(dp_score)
            d_tup["abs_freq"].append(d_freq_corpus["corpus"][tup])
            d_tup["adj_freq"].append(adj_freq)
            d_tup["abs_freq_Lapl"].append(abs_freq_lapl)
            d_tup["adj_freq_Lapl"].append(adj_freq_lapl)

        d_abs_adj[tup] = d_tup

    d_abs_adj_json = {}

    for tup in d_abs_adj:
        d_abs_adj_json[str(tup)] = d_abs_adj[tup]

    fn_d_abs_adj = corpus_name + "_d_freq_abs_adj"
    dump_json_sub1("prep", corpus_name, fn_d_abs_adj, d_abs_adj_json)

    return d_abs_adj

# add adjusted frequencies to frequency dictionary (totals)


def sum_words_desired_pos_abs_adj(corpus_name, d_abs_adj, desired_pos, n_iters):
    l_d_sum_abs_adj = []

    for iteration in range(n_iters):

        d_sum_abs_adj = {"all": {"abs_freq": 0, "adj_freq": 0, "abs_freq_Lapl": 0, "adj_freq_Lapl": 0, "unique": 0}}

        for pos in desired_pos:
            d_sum_abs_adj[pos] = {"abs_freq": 0, "adj_freq": 0, "abs_freq_Lapl": 0, "adj_freq_Lapl": 0, "unique": 0}

        for tup in d_abs_adj:
            pos = tup[1]
            d_sum_abs_adj["all"]["abs_freq"] += d_abs_adj[tup]["abs_freq"][iteration]
            d_sum_abs_adj["all"]["adj_freq"] += d_abs_adj[tup]["adj_freq"][iteration]
            d_sum_abs_adj["all"]["abs_freq_Lapl"] += d_abs_adj[tup]["abs_freq_Lapl"][iteration]
            d_sum_abs_adj["all"]["adj_freq_Lapl"] += d_abs_adj[tup]["adj_freq_Lapl"][iteration]
            d_sum_abs_adj["all"]["unique"] += 1

            d_sum_abs_adj[pos]["abs_freq"] += d_abs_adj[tup]["abs_freq"][iteration]
            d_sum_abs_adj[pos]["adj_freq"] += d_abs_adj[tup]["adj_freq"][iteration]
            d_sum_abs_adj[pos]["abs_freq_Lapl"] += d_abs_adj[tup]["abs_freq_Lapl"][iteration]
            d_sum_abs_adj[pos]["adj_freq_Lapl"] += d_abs_adj[tup]["adj_freq_Lapl"][iteration]
            d_sum_abs_adj[pos]["unique"] += 1

        l_d_sum_abs_adj.append(d_sum_abs_adj)

    fn_d_sum_abs_adj = corpus_name + "_sum_words_desired_POS_abs_adj"
    dump_json_sub1("prep", corpus_name, fn_d_sum_abs_adj, l_d_sum_abs_adj)

    return l_d_sum_abs_adj

# calculate keyness


def keyness_calculation(n_iters, approx, stat_sign_thres, degrs_of_freed, freq_type, keyn_metric, d_abs_adj_sc,
                        d_abs_adj_rc, l_d_sum_abs_adj_sc, l_d_sum_abs_adj_rc):
    l_d_keyn_ranked = []

    for iteration in range(n_iters):
        l_d_keyn_ranked_prov = []

        sum_sc = l_d_sum_abs_adj_sc[iteration]["all"][freq_type]
        sum_rc = l_d_sum_abs_adj_rc[iteration]["all"][freq_type]

        for tup in d_abs_adj_sc:

            freq_sc = d_abs_adj_sc[tup][freq_type][iteration]

            if tup in d_abs_adj_rc:
                freq_rc = d_abs_adj_rc[tup][freq_type][iteration]

            else:

                if freq_type in ["abs_freq", "adj_freq"]:
                    freq_rc = approx
                elif freq_type in ["abs_freq_Lapl", "adj_freq_Lapl"]:
                    freq_rc = 1
                else:
                    raise ValueError("frequency_type is not correctly defined.")

            exp_freq_sc = sum_sc * (freq_sc + freq_rc) / (sum_sc + sum_rc)
            exp_freq_rc = sum_rc * (freq_sc + freq_rc) / (sum_sc + sum_rc)

            norm_freq_1000_sc = freq_sc / sum_sc * 1000
            norm_freq_1000_rc = freq_rc / sum_rc * 1000

            if keyn_metric == "DIFF":
                keyn_score_sc = ((norm_freq_1000_sc - norm_freq_1000_rc) * 100) / norm_freq_1000_rc

            elif keyn_metric == "Ratio":
                keyn_score_sc = norm_freq_1000_sc / norm_freq_1000_rc

            elif keyn_metric == "OddsRatio":
                keyn_score_sc = (freq_sc / (sum_sc - freq_sc)) / (freq_rc / (sum_rc - freq_rc))

            elif keyn_metric == "LogRatio":
                keyn_score_sc = np.log2(norm_freq_1000_sc / norm_freq_1000_rc)

            elif keyn_metric == "DiffCoefficient":
                keyn_score_sc = (norm_freq_1000_sc - norm_freq_1000_rc) / (norm_freq_1000_sc + norm_freq_1000_rc)

            else:
                raise ValueError("keyness_metric is not correctly defined.")

            if freq_sc == 0 or exp_freq_sc == 0:

                if freq_rc == 0 or exp_freq_rc == 0:
                    log_lik = 0
                else:
                    log_lik = 2 * (freq_rc * np.log(freq_rc / exp_freq_rc))

            else:

                if freq_rc == 0 or exp_freq_rc == 0:
                    log_lik = 2 * (freq_sc * np.log(freq_sc / exp_freq_sc))
                else:
                    log_lik = 2 * ((freq_sc * np.log(freq_sc / exp_freq_sc)) + (freq_rc * np.log(freq_rc / exp_freq_rc)))

            bic = log_lik - (degrs_of_freed * np.log(sum_sc + sum_rc))

            d_keyn_ranked_prov = {}

            if bic >= stat_sign_thres:
                d_keyn_ranked_prov["item"] = tup
                d_keyn_ranked_prov["keyn_SC"] = keyn_score_sc
                d_keyn_ranked_prov["freq_SC"] = freq_sc

                l_d_keyn_ranked_prov.append(d_keyn_ranked_prov)

        # $

        sorted_l_d_keyn_ranked = sorted(sorted(
            sorted(l_d_keyn_ranked_prov, key=lambda i: i["item"]), key=lambda i: i["freq_SC"], reverse=True),
            key=lambda i: i["keyn_SC"], reverse=True)  # sort key items by 1) keyness (descending); 2) freq_SC (descending); 3) pos_lem_or_tok (ascending)

        d_keyn_ranked = {}
        ranking_score_abs = len(sorted_l_d_keyn_ranked)

        for dic in sorted_l_d_keyn_ranked:
            tup = dic["item"]
            d_keyn_ranked[tup] = {}
            d_keyn_ranked[tup]["keyn"] = dic["keyn_SC"]
            d_keyn_ranked[tup]["freq_SC"] = dic["freq_SC"]
            d_keyn_ranked[tup]["ranking_score"] = ranking_score_abs / len(sorted_l_d_keyn_ranked) * 100
            ranking_score_abs -= 1

        l_d_keyn_ranked.append(d_keyn_ranked)

    return l_d_keyn_ranked

# $


def results_to_xlsx_per_sc(l_corpora_sc, l_corpora_rc, corpus_name_sc, lem_or_tok, keyn_metric, freq_type,
                           ranking_thresh, l_d_keyn, d_keyn_per_corpus, cps_sc, cps_rc):
    output_direc = "_".join(l_corpora_sc) + "_VS_" + "_".join(l_corpora_rc)
    fn_keyn = corpus_name_sc + "_VS_" + "_".join(l_corpora_rc) + "_keyness_ranked_" + keyn_metric + "_" + freq_type

    if len(l_corpora_rc) == 1:
        n_rc = 1
    else:
        n_rc = len(l_corpora_rc) + 1

    n_rankings_thresh = n_rc * ranking_thresh

    # write final results into XLSX

    if not os.path.isdir(os.path.join(output_direc)):
        os.mkdir(output_direc)

    headers = [lem_or_tok, "POS", "number_values", "average_ranking_score", "average_keyness_score"]

    for corpus in d_keyn_per_corpus.keys():
        headers.append(corpus)

    wb = xlsxwriter.Workbook(os.path.join(output_direc, fn_keyn + ".xlsx"))
    ws1 = wb.add_worksheet("ranking_score_all")
    ws2 = wb.add_worksheet("keyness_all")
    ws3 = wb.add_worksheet("ranking_score_threshold")
    ws4 = wb.add_worksheet("keyness_threshold")
    ws5 = wb.add_worksheet("meta")

    column = 0

    for header in headers:
        ws1.write(0, column, header)
        ws2.write(0, column, header)
        ws3.write(0, column, header)
        ws4.write(0, column, header)
        column += 1

    row_ws_1_and_2 = 1

    for dic in l_d_keyn:
        ws1.write(row_ws_1_and_2, 0, str(dic["item"][0]))
        ws1.write(row_ws_1_and_2, 1, str(dic["item"][1]))
        ws1.write(row_ws_1_and_2, 2, dic["n_rankings"])
        ws1.write(row_ws_1_and_2, 3, dic["ranking_score_avg"])
        ws1.write(row_ws_1_and_2, 4, dic["keyness_score_avg"])

        ws2.write(row_ws_1_and_2, 0, str(dic["item"][0]))
        ws2.write(row_ws_1_and_2, 1, str(dic["item"][1]))
        ws2.write(row_ws_1_and_2, 2, dic["n_rankings"])
        ws2.write(row_ws_1_and_2, 3, dic["ranking_score_avg"])
        ws2.write(row_ws_1_and_2, 4, dic["keyness_score_avg"])

        column_ws = 5

        for corpus in dic["d_keyn"]:
            ranking_score = []
            keyn_score = []
            n_rankings = 0

            for item in dic["d_keyn"][corpus]:

                if item == "NA":
                    pass
                else:
                    ranking_score.append(item["ranking_score"])
                    keyn_score.append(item["keyn"])
                    n_rankings += 1

            if n_rankings == 0:
                ws1.write(row_ws_1_and_2, column_ws, "NA")
                ws2.write(row_ws_1_and_2, column_ws, "NA")
                column_ws += 1

            else:
                ws1.write(row_ws_1_and_2, column_ws, statistics.mean(ranking_score))
                ws2.write(row_ws_1_and_2, column_ws, statistics.mean(keyn_score))
                column_ws += 1

        row_ws_1_and_2 += 1

    row_ws_3_and_4 = 1

    for dic in l_d_keyn:

        if dic["n_rankings"] > n_rankings_thresh:
            ws3.write(row_ws_3_and_4, 0, str(dic["item"][0]))
            ws3.write(row_ws_3_and_4, 1, str(dic["item"][1]))
            ws3.write(row_ws_3_and_4, 2, dic["n_rankings"])
            ws3.write(row_ws_3_and_4, 3, dic["ranking_score_avg"])
            ws3.write(row_ws_3_and_4, 4, dic["keyness_score_avg"])

            ws4.write(row_ws_3_and_4, 0, str(dic["item"][0]))
            ws4.write(row_ws_3_and_4, 1, str(dic["item"][1]))
            ws4.write(row_ws_3_and_4, 2, dic["n_rankings"])
            ws4.write(row_ws_3_and_4, 3, dic["ranking_score_avg"])
            ws4.write(row_ws_3_and_4, 4, dic["keyness_score_avg"])

            column_ws = 5

            for corpus in dic["d_keyn"]:
                ranking_score = []
                keyn_score = []
                n_rankings = 0

                for item in dic["d_keyn"][corpus]:

                    if item == "NA":
                        pass
                    else:
                        ranking_score.append(item["ranking_score"])
                        keyn_score.append(item["keyn"])
                        n_rankings += 1

                if n_rankings == 0:
                    ws3.write(row_ws_3_and_4, column_ws, "NA")
                    ws4.write(row_ws_3_and_4, column_ws, "NA")
                    column_ws += 1

                else:
                    ws3.write(row_ws_3_and_4, column_ws, statistics.mean(ranking_score))
                    ws4.write(row_ws_3_and_4, column_ws, statistics.mean(keyn_score))
                    column_ws += 1

            row_ws_3_and_4 += 1

    ws5.write(0, 0, "name_sc")
    ws5.write(0, 1, corpus_name_sc)
    ws5.write(1, 0, "maintain_subcorpora_sc")
    ws5.write(1, 1, cps_sc)
    ws5.write(2, 0, "name_rc")
    ws5.write(2, 1, "_".join(l_corpora_rc))
    ws5.write(3, 0, "maintain_subcorpora_rc")
    ws5.write(3, 1, cps_rc)

    wb.close()

# $


def results_to_xlsx_overview(l_corpora_sc, l_corpora_rc, lem_or_tok, keyn_metric, freq_type, ranking_thresh,
                             l_d_keyn, d_keyn_overview, cps_sc, cps_rc):
    output_direc = "_".join(l_corpora_sc) + "_VS_" + "_".join(l_corpora_rc)
    fn_keyn = "_".join(l_corpora_sc) + "_VS_" + "_".join(l_corpora_rc) +\
              "_keyness_ranked_overview_" + keyn_metric + "_" + freq_type

    if len(l_corpora_sc) == 1:
        n_sc = 1
    else:
        n_sc = len(l_corpora_sc) + 1

    n_rankings_thresh = n_sc * ranking_thresh

    # write final results into XLSX

    headers = [lem_or_tok, "POS", "number_values", "average_ranking_score", "average_keyness_score"]

    for corpus in d_keyn_overview.keys():
        headers.append(corpus)

    wb = xlsxwriter.Workbook(os.path.join(output_direc, fn_keyn + ".xlsx"))
    ws1 = wb.add_worksheet("ranking_score_all")
    ws2 = wb.add_worksheet("ranking_score_threshold")
    ws3 = wb.add_worksheet("meta")

    column = 0

    for header in headers:
        ws1.write(0, column, header)
        ws2.write(0, column, header)
        column += 1

    row_ws1 = 1

    for dic in l_d_keyn:
        ws1.write(row_ws1, 0, str(dic["item"][0]))
        ws1.write(row_ws1, 1, str(dic["item"][1]))
        ws1.write(row_ws1, 2, dic["n_rankings"])
        ws1.write(row_ws1, 3, dic["ranking_score_avg_avg"])
        ws1.write(row_ws1, 4, dic["keyness_score_avg_avg"])

        column_ws = 5

        for corpus in dic["d_keyn"]:

            if dic["d_keyn"][corpus] == "NA":
                ws1.write(row_ws1, column_ws, "NA")
                column_ws += 1
            else:
                ws1.write(row_ws1, column_ws, dic["d_keyn"][corpus]["ranking_score_avg"])
                column_ws += 1

        row_ws1 += 1

    row_ws2 = 1

    for dic in l_d_keyn:

        if dic["n_rankings"] > n_rankings_thresh:
            ws2.write(row_ws2, 0, str(dic["item"][0]))
            ws2.write(row_ws2, 1, str(dic["item"][1]))
            ws2.write(row_ws2, 2, dic["n_rankings"])
            ws2.write(row_ws2, 3, dic["ranking_score_avg_avg"])
            ws2.write(row_ws2, 4, dic["keyness_score_avg_avg"])

            column_ws = 5

            for corpus in dic["d_keyn"]:

                if dic["d_keyn"][corpus] == "NA":
                    ws2.write(row_ws2, column_ws, "NA")
                    column_ws += 1
                else:
                    ws2.write(row_ws2, column_ws, dic["d_keyn"][corpus]["ranking_score_avg"])
                    column_ws += 1

            row_ws2 += 1

    ws3.write(0, 0, "name_SC")
    ws3.write(0, 1, "_".join(l_corpora_sc))
    ws3.write(1, 0, "maintain_subcorpora_SC")
    ws3.write(1, 1, cps_sc)
    ws3.write(2, 0, "name_RC")
    ws3.write(2, 1, "_".join(l_corpora_rc))
    ws3.write(3, 0, "maintain_subcorpora_RC")
    ws3.write(3, 1, cps_rc)

    wb.close()
    
# STEP_1: convert corpora into frequency dictionaries (data stored per corpus in "prep" folder)


def corpora_to_d_freq(corpus_name, input_type, input_corpus, maintain_subcorpora, mapping_custom_to_ud,
                      mapping_ud_to_custom,  desired_pos, lem_or_tok, div_n_docs_by, n_iters):
    d_freq_corpus, l_d_freq_cps = d_freq(
        corpus_name, input_type, input_corpus, maintain_subcorpora, mapping_custom_to_ud, mapping_ud_to_custom,
        desired_pos, lem_or_tok, div_n_docs_by, n_iters)
    l_d_freq_sum_cps = sum_words_desired_pos(
        corpus_name, d_freq_corpus, maintain_subcorpora, desired_pos, n_iters, l_d_freq_cps)

    return d_freq_corpus, l_d_freq_sum_cps


# STEP_2: store information of last query in meta file (data stored per corpus in "prep" folder)


def meta(corpus_name, maintain_subcorpora, desired_pos, lem_or_tok, div_n_docs_by, n_iters):
    d_meta(corpus_name, maintain_subcorpora, desired_pos, lem_or_tok, div_n_docs_by, n_iters)

# STEP_3: apply dispersion metric (DPnorm; Gries, 2008; Lijffijt & Gries, 2012), calculate adjusted frequencies and
# update frequency dictionaries (data stored per corpus in "prep" folder)


def dispersion(corpus_name, desired_pos, d_freq_corpus, l_d_freq_sum_cps, n_iters):
    d_dp = dp(corpus_name, d_freq_corpus, l_d_freq_sum_cps)
    d_freq_abs_adj_corpus = d_freq_abs_adj(corpus_name, d_freq_corpus, d_dp)
    l_d_sum_abs_adj = sum_words_desired_pos_abs_adj(corpus_name, d_freq_abs_adj_corpus, desired_pos, n_iters)

    return d_freq_abs_adj_corpus, l_d_sum_abs_adj

# STEP_4: calculate keyness (data stored in "[SC]_VS_[RC]" folder)


def keyness(
        n_iters, approx, stat_sign_thresh_bic, degrs_of_freed, freq_type, keyn_metric,
        d_freq_abs_adj_sc, l_d_sum_abs_adj_sc, d_freq_abs_adj_rc, l_d_sum_abs_adj_rc
):
    l_d_keyn_ranked = keyness_calculation(
        n_iters, approx, stat_sign_thresh_bic, degrs_of_freed, freq_type, keyn_metric,
        d_freq_abs_adj_sc, d_freq_abs_adj_rc, l_d_sum_abs_adj_sc, l_d_sum_abs_adj_rc)

    return l_d_keyn_ranked
