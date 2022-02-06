# NLP-Swedish
… allows to estimate CEFR (Common European Framework of References) complexity score of a given word, sentence or text.
CEFR scores come from database created by https://spraakbanken.gu.se/om
https://svn.spraakdata.gu.se/sb-arkiv/pub/lexikon/kelly/kelly.xml

# Requirements
 - pip install -r requirements.txt
 - (python) import stanza
 - (python) stanza.download('sv')
 - Download https://svn.spraakdata.gu.se/sb-arkiv/pub/lexikon/kelly/kelly.xml

# How do I use it?
cefr.find('bil')  # returns pd.DataFrame
cefr.Complexity.word('pröva')  # returns CEFR score
cefr.Complexity.sentence('Jag kör bil.')  # returns CEFR score
cefr.Complexity.text('Jag kör bil. Barn kör bilar.')  # returns CEFR score
