import os
import pytest

import cefr

def test_kelly_xml_is_present():
    assert os.path.exists(cefr.LEX_KELLY)

def test_cefr_word_present():
    assert cefr.find('bil').index.size == 1
    assert cefr.find('för').index.size == 4

def test_complexity_word_raise_word_not_found():
    w = cefr.nlp('bil').sentences[0].words[0]
    w.lemma = 'boooooooooo'  # corrupt lemma
    cefr.fail_on_missing_lemma = True
    with pytest.raises(cefr.CefrLemmaNotFoundException):
        cefr._complexity_word(w)

def test_cefr_complexity_word():
    words = {
        'bil': 1,
        'bilar': 1,
        'prövade': 2,
        'prövat': 2
    }
    for w, score in words.items():
        assert cefr.Complexity.word(w) == score

def test_cefr_complexity_simple_sentence():
    # all words have only one entry
    sentencies = {
        'Kvinna kör bil.': 1,
        'Kvinna körde bil.': 1,
        'Kvinna körde bilar': 1,
    }
    for sent, score in sentencies.items():
        assert cefr.Complexity.sentence(sent) == score

def test_cefr_complexity_complex_sentence():
    # some words have several entries
    sentencies = {
        'Man kör bil.': 1,
        'En kvinna körde en bil': 1,
        'Många barn kör bil.': 1
    }
    for sent, score in sentencies.items():
        assert cefr.Complexity.sentence(sent) == score

def test_cefr_complexity_text():
    txt = 'En man kör en bil. Många barn kör bil.'
    assert cefr.Complexity.text(txt) == 1

def test_cefr_complexity_sentence_with_unknown_words():
    cefr.fail_on_missing_lemma = False
    s = ('Sverige är en konstitutionell monarki'
         ' med parlamentarisk demokrati och utvecklad ekonomi.')
    assert cefr.Complexity.sentence(s) == 1.8888888888888888