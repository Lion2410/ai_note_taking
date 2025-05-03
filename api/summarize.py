import os
import nltk

# Get the path to nltk_data from the environment variable, defaulting to the local directory
nltk_data_dir = os.getenv('NLTK_DATA', os.path.join(os.getcwd(), 'nltk_data'))

# Add this directory to NLTK's search path
nltk.data.path.append(nltk_data_dir)

# Download 'punkt' if it's not already available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', download_dir=nltk_data_dir)


from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

LANGUAGE = "english"  # Language for summarization
SENTENCES_COUNT = 5  # Number of sentences for the summary

def summarize_text(text):
    """
    This function takes a text string as input, tokenizes it, summarizes it, and returns the summary.
    :param text: The text to summarize
    :return: A summarized version of the input text
    """
    # Parsing the text into a format compatible with Sumy summarizers
    parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
    
    # Initialize the stemmer for the specified language
    stemmer = Stemmer(LANGUAGE)

    # Initialize the summarizer (LexRankSummarizer)
    summarizer = LexRankSummarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    # Generate the summary
    summary = summarizer(parser.document, SENTENCES_COUNT)
    
    # Join the summary into a single string
    summarized_text = ' '.join(str(sentence) for sentence in summary)

    # If the summary is empty, return a default message
    return summarized_text if summarized_text else "Summary could not be generated."
