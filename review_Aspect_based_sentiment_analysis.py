import warnings
import pandas as pd
import numpy as np
import spacy
from pyabsa.tasks.AspectPolarityClassification import SentimentClassifier
from nltk.tokenize import sent_tokenize
import nltk
nltk.download('punkt')
warnings.filterwarnings("ignore")

ner = spacy.load(r"./model-best")

clf = SentimentClassifier("multilingual")


def absa(input):
    '''
    Function absa mean aspect based sentiment analysis,
    it will take the list of reviews and divide them into
    sentences, then extract the food as an aspect and 
    output the aspect id from which review, its sentiment
    and its confidence.

    Parameters:
        reviews: list
            A list of review, for each review can contain
            multiple sentences and aspects.

    Returns:
        output: DataFrame
            A DataFrame contain 4 features, review id, aspect,
            sentiment and confidence
    '''

    output = pd.DataFrame(
        columns=['review_id', 'dish', 'sentiment', 'confidence'])

    for i, doc in enumerate(input):

        sentences = sent_tokenize(doc)

        for sentence in sentences:
            result = ner(sentence)
            sentens = sentence

            for ent in reversed(result.ents):
                if ent.label_ == 'DISH':
                    aspect = f'[B-ASP]{ent.text}[E-ASP]'
                    # sentence = sentence.replace(ent.text, f'[B-ASP]{ent.text}[E-ASP]')
                    sentens = sentens[:ent.start_char] + \
                        aspect + sentens[ent.end_char:]

            if 'ASP' in sentens:
                senti = clf.predict(sentens,
                                    save_result=False,
                                    print_result=False,
                                    ignore_error=True)

                if senti['aspect'] != ['Global Sentiment']:
                    for j in range(len(senti['aspect'])):
                        output = output.append({'review_id': i,
                                                'dish': senti['aspect'][j],
                                                'sentiment': senti['sentiment'][j],
                                                'confidence': senti['confidence'][j]},
                                               ignore_index=True)

    return output
