import math
from collections import defaultdict

class TFIDFCalculator:
    """TF-IDF calculator for document ranking"""
    
    @staticmethod
    def calculate_tf_idf(inverted_index, doc_frequencies, total_docs, doc_lengths):
        """Calculate TF-IDF for all terms in the index"""
        for term, doc_dict in inverted_index.items():
            df = doc_frequencies[term]
            # Smoothed IDF to avoid division by zero
            idf = math.log((total_docs + 1) / (df + 1)) + 1
            
            for doc_id, term_info in doc_dict.items():
                tf = term_info['tf']
                # Normalized TF
                normalized_tf = tf / doc_lengths[doc_id] if doc_lengths[doc_id] > 0 else 0
                # TF-IDF
                tf_idf = normalized_tf * idf
                term_info['tf_idf'] = tf_idf
        
        return inverted_index
    
    @staticmethod
    def calculate_tf_idf_for_query(query_terms, doc_terms, doc_frequencies, total_docs):
        """Calculate TF-IDF vector for a query"""
        term_freq = {}
        for term in query_terms:
            term_freq[term] = term_freq.get(term, 0) + 1
        
        vector = {}
        doc_len = len(query_terms)
        
        for term, tf in term_freq.items():
            df = doc_frequencies.get(term, 0)
            if df > 0:
                idf = math.log((total_docs + 1) / (df + 1)) + 1
                normalized_tf = tf / doc_len if doc_len > 0 else 0
                vector[term] = normalized_tf * idf
        
        return vector