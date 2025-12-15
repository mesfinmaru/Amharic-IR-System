import json
import re
import os

class AmharicTextUtils:
    """Utility class for Amharic text processing"""
    
    # Amharic stop words
    AMHARIC_STOPWORDS = {
        'ውስጥ', 'እና', 'ወደ', 'ከ', 'ላይ', 'በ', 'ን', 'ነበር', 'ነው', 'አይደለም',
        'ማ', 'ም', 'ኡ', 'ው', 'ዎች', 'ቸው', 'ዋ', 'ያ', 'ስ', 'ምን', 'የ', 'ኢ', 'ሲ',
        'አለ', 'ቢ', 'እንደ', 'ለ', 'ነገር', 'ይ', 'ከነ', 'ያለ', 'የሚ', 'እየ', 'በሚ',
        'የነ', 'እስከ', 'ስለ', 'ውጪ', 'አብሮ', 'አብረው', 'ከሆነ', 'ከሆኑ', 'ሆነ',
        'ሆኑ', 'ከሆነት', 'ስለሆነ', 'ስለሆኑ', 'ስለሆነት'
    }
    
    # Stemming rules
    PREFIXES = ['የ', 'በ', 'ለ', 'ከ', 'እንደ', 'ስለ', 'ያለ', 'ከሚ', 'በሚ', 'ለሚ']
    SUFFIXES = ['ዎች', 'ው', 'ዋ', 'ዎ', 'ቸው', 'ያችሁ', 'ያችን', 'ህ', 'ሽ', 'ን']
    
    @staticmethod
    def clean_text(text):
        """Clean Amharic text - remove punctuation and normalize"""
        amharic_punct = '፡።፣፤፥፦፧፨!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
        text = re.sub(f'[{re.escape(amharic_punct)}]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    @staticmethod
    def stem_amharic_word(word):
        """Simple stemmer for Amharic words"""
        if len(word) < 3:
            return word
            
        original_word = word
        
        # Remove prefixes
        for prefix in AmharicTextUtils.PREFIXES:
            if word.startswith(prefix) and len(word) > len(prefix) + 1:
                word = word[len(prefix):]
                break
                
        # Remove suffixes
        for suffix in AmharicTextUtils.SUFFIXES:
            if word.endswith(suffix) and len(word) > len(suffix) + 1:
                word = word[:-len(suffix)]
                break
                
        if len(word) < 2:
            return original_word
            
        return word