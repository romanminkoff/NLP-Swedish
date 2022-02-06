import pandas as pd
import stanza

nlp = stanza.Pipeline('sv')

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

class CefrWordNotFoundException(Exception):
    pass

def _complexity_word(w: stanza.models.common.doc.Word):
    kelly_df = find(w.lemma)
    if kelly_df.index.size == 0:
        raise CefrWordNotFoundException(w.lemma)
    
    for _, row in kelly_df.iterrows():
        if w.upos == kelly_to_stanza_pos[row.pos]:
            return row.cefr
    
    # PoS is missing, so return cefr score of the most frequent case
    return kelly_df.iloc[0].cefr

def _complexity_sentence(s: stanza.models.common.doc.Sentence):
    skip_PoS = ['PUNCT', 'NUM', 'PROPN']
    words_cnt = 0
    score = 0
    for w in s.words:
        if w.upos in skip_PoS:
            continue
        idx = _complexity_word(w)
        score += idx
        words_cnt += 1
    mean_score = score/words_cnt
    return mean_score

def _complexity_text(t: stanza.models.common.doc.Document):
    sent_cnt = 0
    score = 0
    for s in t.sentences:
        idx = _complexity_sentence(s)
        score += idx
        sent_cnt += 1
    mean_score = score/sent_cnt
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
