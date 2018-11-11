from horopter.parsing.cleaners import TextCleaner


class PolarityAnalyzer:
    def __init__(self, classifier=None, vectorizer=None, morph=None):
        self.classifier = classifier
        self.vectorizer = vectorizer
        self.morph = morph
    
    
    def lemmatize(self, string):
        lemmatized = [self.morph.parse(w)[0].normal_form 
                      for w in string.split()]
        return ' '.join(lemmatized)
    
    
    def preprocess(self, text):
        cleaned_string = self.lemmatize(TextCleaner.cleanse('\W', text))
        return self.vectorizer.transform([cleaned_string])
    
    
    def predict(self, text):
        return self.classifier.predict(self.preprocess(text))[0]