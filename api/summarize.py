import nltk

# Ensure that punkt is downloaded before using it
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

LANGUAGE = "english"
SENTENCES_COUNT = 5

def summarize_text(text):
    parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = LexRankSummarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    summary = summarizer(parser.document, SENTENCES_COUNT)
    summarized_text = ' '.join(str(sentence) for sentence in summary)

    return summarized_text if summarized_text else "Summary could not be generated."
