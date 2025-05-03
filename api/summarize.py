import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

# Download the punkt tokenizer data (only run once)
nltk.download('punkt', quiet=True)

LANGUAGE = "english"
SENTENCES_COUNT = 5

def summarize_text(text):
    if not text or text.isspace():  # Check if text is empty or only spaces
        return "No content to summarize."

    # Prepare the text for summarization
    parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    # Initialize LexRank summarizer
    summarizer = LexRankSummarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    # Generate the summary
    summary = summarizer(parser.document, SENTENCES_COUNT)
    summarized_text = ' '.join(str(sentence) for sentence in summary)

    return summarized_text if summarized_text else "Summary could not be generated."

