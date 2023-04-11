import Main.constants as CONS
from Main.classes import ExtractedObject
import os.path
import json
import spacy
from spacy.tokens import Doc, Span, Token
import nltk
from nltk.corpus import wordnet as wn

import time
import datetime


# Input: corpus = path to corpus file. Must be a Json file
# Input: language = language of entries in corpus file. Must be in CONS.LANG and have a dict in CONS.CATEGORIES
#        under file constants.py
# Input: category = classification category to use during processing. Must be in CONS.CATEGORIES under file constants.py
# Input: results_name_file = name and/or path to the results file. Must not include the file extension
# Input: silent = enable/disable flavour text during processing. Default: False
# Input: info_loop = used only if not silent, every how many cycles print looping flavour texts. Default: 1000
# Input: multi_out = return in output two different files, one verbose (txt file) and one structured for further
#        analysis (json file). Default: False
# Input: verb_out = considered only if multi_out is False. Select which output you want: "False" for file strict for
#        analysis (json one), or "True" for verbose file (txt one). Default: False
def spacy_extraction(corpus: str, language: str, category: str, results_name_file: str,
                     silent: bool = False, info_loop: int = 1000,
                     multi_out: bool = False, verb_out: bool = False) -> None:
    # Consistency checks
    if not os.path.isfile(corpus):
        print(f"Corpus '{corpus}' is not a path to a file.\n"
              f"Try another one.")
        return

    if corpus.split("/")[-1].split(".")[-1] != "json":
        print(f"File '{corpus.split('/')[-1]}' is not a JSON file.\n"
              f"Corpus rejected.")
        return

    language = language.upper()
    if language not in CONS.LANG:
        lang_str = ", ".join(list(CONS.LANG.keys()))
        print(f"Language '{language}' is not supported.\n"
              f"Possible languages are: {lang_str}.")
        return

    category = category.capitalize()
    if category not in CONS.CATEGORIES:
        cats_str = ", ".join(list(CONS.CATEGORIES.keys()))
        print(f"Category '{category}' is not supported.\n"
              f"Possible categories are: {cats_str}.")
        return

    if language[:2] not in CONS.CATEGORIES[category]:
        lang_str = ", ".join(list(CONS.CATEGORIES[category].keys()))
        print(f"Language '{language[:2]}' is not supported for category '{category}'.\n"
              f"Possible languages are: {lang_str}.")
        return

    if not silent:
        flavour_text(language[:2], "Param_check_end")

    # Install spaCy pipeline
    if not spacy.util.is_package(CONS.LANG[language]["spaCy"]):
        spacy.cli.download(CONS.LANG[language]["spaCy"])

    # Install nltk libraries
    nltk_dl = nltk.downloader.Downloader()
    for nltk_ver in ['wordnet', 'omw-1.4']:
        if not nltk_dl.is_installed(nltk_ver):
            nltk.download(nltk_ver)

    with open(corpus, encoding="utf-8") as in_file:
        _ = in_file.readline()
        d_set = "[" + in_file.read()
        d_set = d_set[:-1]

    # As json dict
    d_set = json.loads(d_set)

    if not silent:
        flavour_text(language[:2], "Data_load_end", str(len(d_set)))

    # Tagging with spaCy pipeline
    nlp = spacy.load(CONS.LANG[language]["spaCy"])
    dobj_list = []
    for i in range(len(d_set)):
        recipe = d_set[i]["Method"]

        # Extraction
        doc = nlp(recipe)
        dobj_list += __get_direct_object_pairs(doc=doc, language=language[:2])

        if not silent and ((i + 1) % info_loop == 0):
            flavour_text(language[:2], "Elab_loop", str(i + 1))

    if not silent:
        flavour_text(language[:2], "Extract_end", str(len(dobj_list)))

    # Categorization with NLTK
    i = 0
    for dobj in dobj_list:
        hypers = __get_obj_hypernames(dobj=dobj.get_lemma(), language=language)
        check_category(language=language, category=category, dobj=dobj, hypers=hypers)
        i += 1

        if not silent and ((i + 1) % info_loop == 0):
            flavour_text(language[:2], "Categ_loop", str(i + 1))

    if not silent:
        flavour_text(language[:2], "Categ_end")

    # Analytic (json) output
    if multi_out or not verb_out:
        with open(results_name_file + ".json", "w") as out_file:
            json_dump = []
            for element in dobj_list:
                supp_dict = dict()

                supp_dict["Lemma"] = element.get_lemma()
                supp_dict["Object"] = element.get_direct_object()
                supp_dict["Verb"] = element.get_verb()
                supp_dict["Category"] = element.get_best_hyper()[0]

                json_dump.append(supp_dict)

            out_file.write(json.dumps(json_dump).replace("}, {", "},\n{"))
            pass

    # Verbose (txt) output
    if multi_out or verb_out:
        with open(results_name_file + ".txt", "w") as out_file:
            out_file.write("Reference dataset: " + corpus.split("/")[0] + "\n\n")
            for element in dobj_list:
                out_file.write(f"For [{element.get_verb()} - {element.get_lemma()} ({element.get_direct_object()})]"
                               f" categories are:\n")

                supp = element.get_hypers()
                best = element.get_best_hyper()
                if supp:
                    for item in element.get_hypers():
                        b = ""
                        if item[0] == best[0]:
                            b = "(*)"

                        name = "-" + item[0] + b
                        fixed = 28
                        j = (fixed - len(name)) // 4 + ((fixed - len(name)) % 4 > 0)
                        for i in range(1, j):
                            name += "\t"

                        out_file.write(f"{name}: [{item[1]}], Simil = {round(item[2], 5)}\n")
                else:
                    out_file.write("-Other\n")

                out_file.write("\n")


# Input: doc = a SpaCy Doc containing an entire phrase
# Input: nlp = spaCy pipeline
# Output: a list of direct objects, each in a ExtractedObjects
def __get_direct_object_pairs(doc: Doc, language: str) -> [ExtractedObject]:
    dobj_list = []
    dir_obj = []
    for token in doc:
        # Check dependency tag
        if token.dep_ == "dobj" or token.dep_ == "obj":

            # Extract direct object subtree
            subtree = list(token.subtree)
            start = subtree[0].i
            end = subtree[-1].i + 1
            dir_obj = __refine_direct_object(dobj=doc[start:end], last_obj=dir_obj)

            head_verb = token.head
            while head_verb.pos_ != "VERB" and head_verb.lemma_ != head_verb.head.lemma_:
                head_verb = head_verb.head

            # Extract verb
            if head_verb.pos_ == "VERB":
                if language == "EN":
                    ref_verb = __check_modal_verb(head=head_verb)
                else:
                    ref_verb = head_verb.lemma_
            else:
                ref_verb = "xx"

            # Add pair
            for element in dir_obj:
                dobj_list.append(ExtractedObject(element[0], element[1], ref_verb))
    return dobj_list


# Input: dobj = a SpaCy Span containing a complex direct object
# Input: last_obj = list of the direct objects from the previous analysis (fallback in case of pronoun)
# Output: a list of string, each is a direct object
def __refine_direct_object(dobj: Span, last_obj: [str]) -> [str, str]:
    sub_phrases = [[]]
    index = 0
    skipped_pos = ["DET", "PUNCT", "VERB", "SYM"]
    direct_object = []

    for token in dobj:
        # If a conjunction or specifically a comma, skip token and move saving to the next section
        if "CONJ" in token.pos_ or token.text == ",":
            if sub_phrases[index]:
                sub_phrases.append([])
                index += 1

        # If a determiner, a punctuation or a number, skip token
        elif token.pos_ in skipped_pos:
            pass

        # Basic rule: save token in the current section of the sub-phrases
        else:
            sub_phrases[index].append(token)

    # Create pair lemma-text
    for sub_obj in sub_phrases:
        # main_lemma = ""

        if len(sub_obj) > 1:
            text = [token.text for token in sub_obj]
            text = " ".join(text)

            # If the subtree has a numeral, then is probably an ingredient with measurement,
            # like "1 cup flour" or "2 tbsp water". So we extract the root as main ingredient
            t = [token for token in sub_obj if token.pos_ == "NUM"]
            has_num = True if t else False

            # If one of the terms in sentence is a compound, then is probably a type of something,
            # like "red pepper" or "soy sauce". So we have to get the important part of it
            tokens = [token for token in sub_obj if token.dep_ == "compound"]
            if tokens and not has_num:
                main_lemma = tokens[0].lemma_

            # Base case (has numeral or no compound element): pick the sub-sentence's root as main lemma
            else:
                head = [token for token in sub_obj if token.head.text not in text]
                if len(head):
                    main_lemma = head[0].lemma_
                else:
                    main_lemma = ""

        elif len(sub_obj) == 1:
            sub_obj = sub_obj[0]
            text = sub_obj.text

            # If pronoun, check number
            if sub_obj.pos_ == "PRON":
                if sub_obj.morph.get("Number") == "Sing":
                    # If pronoun is singular, change lemma with that in the last added pair
                    main_lemma = last_obj[-1][0]
                else:
                    # If pronoun is plural, add all the last lemmas as new pairs, with the current text
                    main_lemma = [item[0] for item in last_obj]

            else:
                main_lemma = sub_obj.lemma_
        else:
            main_lemma = ""
            text = ""

        if isinstance(main_lemma, list):
            for item in main_lemma:
                direct_object.append((item, text))
        elif main_lemma != "":
            direct_object.append((main_lemma, text))

    return direct_object


# Input: head = a SpaCy Token containing a verb
# Output: a string containing a verb (or modular verb)
def __check_modal_verb(head: Token) -> str:
    verb = head.lemma_

    for child in head.children:
        if child.i == head.i + 1 and "ADV" in child.pos_:
            verb += f" {child.lemma_}"

    return verb


# Input: dobj = a string containing a noun
# Input depth = an integer, representing hypernyms research depth (default: 3)
# Output: a list of tuples string-integer, with all the found hypernyms and their depth
def __get_obj_hypernames(dobj: str, language: str) -> [(str, int)]:
    synsets = wn.synsets(dobj, pos=wn.NOUN, lang=CONS.LANG[language]["nltk"])
    hyper_list = []

    # For each definition, pick all hypernyms within a specified depth
    for ss in synsets:
        hn = [(item[0].lemma_names(lang=CONS.LANG[language]["nltk"]), item[1])
              for item in ss.hypernym_distances()
              if 0 < item[1]]

        for (hn_list, depth) in hn:
            for element in hn_list:
                hyper_list.append((element.capitalize(), depth))  # Saves also the depth for later use
    return hyper_list


# Input: language = a string containing one of the supported languages in the constrains
# Input: category = a string containing one of the supported categories in the constrains
# Input: dobj = an ExtractedObject with the direct object to be examined
# Input: hypers = a list of tuples string-integer, containing all the possibles hypernyms of the dobj, an the depth
#        at which they were found
# Output: None, as all confirmed categories are saved in the dobj
def check_category(language: str, category: str, dobj: ExtractedObject, hypers: [(str, int)]) -> None:
    true_cats = []

    # Looping through terms in the specified category
    for cat in CONS.CATEGORIES[category][language[:2]]:
        depths = [item[1] for item in hypers if item[0] == cat]
        if len(depths):
            min_depth = min(depths)
        else:
            min_depth = 0

        # Add only the element with the lowest depth
        # If 0, this category is not in the hypernyms, so skip it
        if min_depth > 0:
            word = wn.synsets(dobj.get_lemma(), pos=wn.NOUN, lang=CONS.LANG[language]["nltk"])[0]
            hyper = wn.synsets(cat.lower(), pos=wn.NOUN, lang=CONS.LANG[language]["nltk"])[0]
            simil = word.path_similarity(hyper)
            true_cats.append((cat, min_depth, simil))

    true_cats.sort(key=lambda x: x[1])

    for element in true_cats:
        dobj.add_hyper(element[0], element[1], element[2])


# Input: language = language of the flavour text
# Input: number = the entry to print
# Output: None, as this function is just to print flavour text in the console
def flavour_text(language: str, code: str, extra="") -> None:
    if language not in CONS.FLAVOUR_TEXT:
        language = "EN"

    string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " - " + CONS.FLAVOUR_TEXT[language][code]
    if extra != "":
        print(string.format(extra))
    else:
        print(string)


if __name__ == "__main__":
    # print(f"Start time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    categ = "Food"

    # corpus_name = "Dataset/Meals and their recipes to follow in cooking/json_data.json"   # 9 entries
    # corpus_name = "Dataset/test_corpus_EN.json"
    corpus_name = "Dataset/test_corpus_IT.json"
    # corpus_name = "Dataset/Food Recipe dataset/json_data.json"                            # 82k entries
    # corpus_name = "Dataset/Recipe Ingredients and Reviews/json_data.json"                 # 12.3k entries
    # corpus_name = "Dataset/Christmas Recipes/json_data.json"                              # 1.6k entries

    # lng = "EN4"
    # lng = "IT3"

    # results_name = "Output/Res_EN"
    # results_name = "test_res"
    # results_name = "long_res"
    # results_name = "Output/Refine_Analysis/ver_5"

    '''
    # st_t = time.time()
    spacy_extraction(corpus=corpus_name, language=lng, category=categ, results_name_file=results_name,
                     silent=False, info_loop=2500, multi_out=False, verb_out=True)

    # et_t = time.time()
    # elapsed_time_t = et_t - st_t
    # pr_time_t = time.strftime('%H:%M:%S', time.gmtime(elapsed_time_t)) + "." + str(elapsed_time_t).split(".")[1][:3]

    # print(f"End time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    # print(f"---Execution time of elaboration: {pr_time_t}\n")
    '''

    rng_IT = range(1, 4)
    rng_EN = range(1, 5)
    for i in rng_IT:

        # lng = f"EN{i}"
        # results_name = f"Res_EN_{i}"

        lng = f"IT{i}"
        results_name = f"Res_IT_{i}"

        # st_t = time.time()
        spacy_extraction(corpus=corpus_name, language=lng, category=categ, results_name_file=results_name,
                         multi_out=True, verb_out=False)
        # et_t = time.time()
        # elapsed_time_t = et_t - st_t
        # pr_time_t = time.strftime('%H:%M:%S', time.gmtime(elapsed_time_t)) +
        # "." + str(elapsed_time_t).split(".")[1][:3]

        # print(f"---Execution time of elaboration {i}: {pr_time_t}\n")
    #'''