import pdb
import re

import pytest

from helpers import run_command_and_get_result

DEBUG = False

"""
Attack command-line tests in the format (name, args, sample_output_file)
"""

attack_test_params = [
    #
    # test loading an attack from file
    #
    (
        "attack_from_file",
        (
            "textattack attack --model cnn-imdb "
            "--attack-from-file tests/sample_inputs/attack_from_file.py:Attack "
            "--num-examples 2  --num-examples-offset 18 --attack-n"
        ),
        "tests/sample_outputs/run_attack_from_file.txt",
    ),
    #
    # test interactive mode
    #
    (
        "interactive_mode",
        (
            'printf "All that glitters is not gold\nq\n"',
            "textattack attack --recipe textfooler --model bert-base-uncased-imdb --interactive",
        ),
        "tests/sample_outputs/interactive_mode.txt",
    ),
    #
    # test loading an attack from the transformers model hub
    #
    (
        "attack_from_transformers",
        (
            "textattack attack --model-from-huggingface "
            "distilbert-base-uncased-finetuned-sst-2-english "
            "--dataset-from-nlp glue:sst2:train --recipe deepwordbug --num-examples 3"
        ),
        "tests/sample_outputs/run_attack_transformers_nlp.txt",
    ),
    #
    # test running an attack by loading a model and dataset from file
    #
    (
        "load_model_and_dataset_from_file",
        (
            "textattack attack "
            "--model-from-file tests/sample_inputs/sst_model_and_dataset.py "
            "--dataset-from-file tests/sample_inputs/sst_model_and_dataset.py "
            "--recipe deepwordbug --num-examples 3"
        ),
        "tests/sample_outputs/run_attack_transformers_nlp.txt",
    ),
    #
    # test hotflip on 10 samples from LSTM MR
    #
    (
        "run_attack_hotflip_lstm_mr_4",
        (
            "textattack attack --model lstm-mr --recipe hotflip "
            "--num-examples 4 --num-examples-offset 3"
        ),
        "tests/sample_outputs/run_attack_hotflip_lstm_mr_4.txt",
    ),
    #
    # test: run_attack deepwordbug attack on 10 samples from LSTM MR
    #
    (
        "run_attack_deepwordbug_lstm_mr_2",
        (
            "textattack attack --model lstm-mr --recipe deepwordbug --num-examples 2 --attack-n"
        ),
        "tests/sample_outputs/run_attack_deepwordbug_lstm_mr_2.txt",
    ),
    #
    # test: run_attack targeted classification of class 2 on BERT MNLI with enable_csv
    #   and attack_n set, using the WordNet transformation and beam search with
    #   beam width 2, using language tool constraint, on 10 samples
    #                   (takes about 72s)
    #
    (
        "run_attack_targeted_mnli_misc",
        (
            "textattack attack --attack-n --goal-function targeted-classification:target_class=2 "
            "--enable-csv --model bert-base-uncased-mnli --num-examples 2 --attack-n --transformation word-swap-wordnet "
            "--constraints lang-tool repeat stopword --search beam-search:beam_width=2"
        ),
        "tests/sample_outputs/run_attack_targetedclassification2_wordnet_langtool_enable_csv_beamsearch2_attack_n.txt",
    ),
    #
    # fmt: off
    # test: run_attack untargeted classification on BERT MR using word embedding transformation and greedy-word-WIR search
    #   using Flair's part-of-speech tagger as constraint.
    #
    (
        "run_attack_flair_pos_tagger_bert_score",
        (
            "textattack attack --model bert-base-uncased-mr --search greedy-word-wir --transformation word-swap-embedding "
            "--constraints repeat stopword bert-score:min_bert_score=0.8 part-of-speech:tagger_type=\\'flair\\' "
            "--num-examples 4 --num-examples-offset 10"
        ),
        "tests/sample_outputs/run_attack_flair_pos_tagger_bert_score.txt",
    ),
    # fmt: on
    #
]


@pytest.mark.parametrize("name, command, sample_output_file", attack_test_params)
@pytest.mark.slow
def test_command_line_attack(name, command, sample_output_file):
    """ Runs attack tests and compares their outputs to a reference file.
    """
    # read in file and create regex
    desired_output = open(sample_output_file, "r").read().strip()
    print("desired_output.encoded =>", desired_output.encode())
    print("desired_output =>", desired_output)
    # regex in sample file look like /.*/
    # / is escaped in python 3.6, but not 3.7+, so we support both
    desired_re = (
        re.escape(desired_output)
        .replace("/\\.\\*/", ".*")
        .replace("\\/\\.\\*\\/", ".*")
    )
    result = run_command_and_get_result(command)
    # get output and check match
    assert result.stdout is not None
    stdout = result.stdout.decode().strip()
    print("stdout.encoded =>", result.stdout)
    print("stdout =>", stdout)
    assert result.stderr is not None
    stderr = result.stderr.decode().strip()
    print("stderr =>", stderr)

    if DEBUG and not re.match(desired_re, stdout, flags=re.S):
        pdb.set_trace()
    assert re.match(desired_re, stdout, flags=re.S)
