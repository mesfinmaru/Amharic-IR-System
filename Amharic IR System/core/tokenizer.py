from .utils import AmharicTextUtils
from collections import defaultdict

class AmharicTokenizer:
    """Tokenizer for Amharic text"""
    
    def __init__(self, custom_stopwords=None):
        self.stopwords = AmharicTextUtils.AMHARIC_STOPWORDS.copy()
        if custom_stopwords:
            self.stopwords.update(custom_stopwords)
    
    def tokenize(self, text, stem=True):
        """Tokenize Amharic text with optional stemming"""
        text = AmharicTextUtils.clean_text(text)
        tokens = text.split()
        
        processed_tokens = []
        for token in tokens:
            if not any('\u1200' <= c <= '\u137F' for c in token):
                continue
                
            if token in self.stopwords:
                continue
                
            if stem:
                token = AmharicTextUtils.stem_amharic_word(token)
                
            if token and len(token) > 1:
                processed_tokens.append(token)
                
        return processed_tokens
    
    def tokenize_with_positions(self, text, stem=True):
        """Tokenize text and return tokens with their positions"""
        text = AmharicTextUtils.clean_text(text)
        tokens = text.split()
        
        processed_tokens = []
        position = 0
        
        for token in tokens:
            if not any('\u1200' <= c <= '\u137F' for c in token):
                position += 1
                continue
                
            if token in self.stopwords:
                position += 1
                continue
                
            if stem:
                token = AmharicTextUtils.stem_amharic_word(token)
                
            if token and len(token) > 1:
                processed_tokens.append((token, position))
                
            position += 1
                
        return processed_tokens