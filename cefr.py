import pandas as pd
import stanza

nlp = stanza.Pipeline('sv')

verbose = False
fail_on_missing_lemma = False
round_ndigits = 1

LEX_KELLY = 'kelly.xml'

class _Cefr:
    def __init__(self):
        self.k = self._load_kelly()

    def _load_kelly(self):
        k = pd.read_xml(LEX_KELLY, encoding='utf-8')
        del k['id']
        k['lemma'] = k.saldo.str.split('.', expand=True)[0]
        return k

_cefr = _Cefr()

def find(word):
    return _cefr.k[(_cefr.k.lemma == word) | (_cefr.k.gf == word)]


kelly_to_stanza_pos = {
    'adjective': 'ADJ',
    'adverb': 'ADV',
    'aux verb': 'AUX',
    'conj': 'CCONJ',
    'det': 'DET',
    'interj': 'INTJ',
    'noun': 'NOUN',
    'noun-en': 'NOUN',
    'noun-en/-ett': 'NOUN',
    'noun-ett': 'NOUN',
    'numeral': 'NUM',
    # only one 'particip' word in Kelly.xml: "stängd stänga..3 particip"
    'particip': 'VERB',
    'particle': 'PART',
    # ADP is "a cover term for prepositions and postpositions".
    # see https://universaldependencies.org/u/pos/ADP.html
    'prep': 'ADP',
    'pronoun': 'PRON',
    'proper name': 'PROPN',
    'subj': 'SCONJ',
    'verb': 'VERB'
}

class CefrLemmaNotFoundException(Exception):
    pass

def _round(n):
    return round(n, round_ndigits)

def _verbose(s):
    if verbose:
        print(f'[CEFR] {s}')

def _match_upos(df, w):
    for _, row in df.iterrows():
        if w.upos == kelly_to_stanza_pos[row.pos]:
            return row.cefr

def _cefr_score(w: stanza.models.common.doc.Word):
    lemmas_df = find(w.lemma)
    if len(lemmas_df.index):
        if not (score := _match_upos(lemmas_df, w)):
            # PoS is missing, so return cefr score of the most frequent case
            score = lemmas_df.iloc[0].cefr
        return score

def _complexity_word(w: stanza.models.common.doc.Word):
    if score := _cefr_score(w):
        _verbose(f'{w.text}: {score}')
        return score

    if fail_on_missing_lemma:
        raise CefrLemmaNotFoundException(f'{w.text}, lemma: {w.lemma}')
    else:
        _verbose(f'skipping word. Lemma not found for: {w.text}')

def _complexity_sentence(s: stanza.models.common.doc.Sentence):
    skip_PoS = ['PUNCT', 'NUM', 'PROPN']
    words_cnt = 0
    score = 0
    for w in s.words:
        if w.upos in skip_PoS:
            continue
        if idx := _complexity_word(w):
            score += idx
            words_cnt += 1
    if words_cnt:
        mean_score = _round(score/words_cnt)
        _verbose(f'Sentence score: {mean_score}')
        return mean_score

def _complexity_text(t: stanza.models.common.doc.Document):
    sent_cnt = 0
    score = 0
    for s in t.sentences:
        if idx := _complexity_sentence(s):
            score += idx
            sent_cnt += 1
    if sent_cnt:
        mean_score = _round(score/sent_cnt)
        _verbose(f'Text score: {mean_score}')
        return mean_score


class Complexity:
    @staticmethod
    def word(w):
        _w = nlp(w).sentences[0].words[0]
        return _complexity_word(_w)

    @staticmethod
    def sentence(s):
        _s = nlp(s).sentences[0]
        return _complexity_sentence(_s)
    
    @staticmethod
    def text(t):
        return _complexity_text(nlp(t))
