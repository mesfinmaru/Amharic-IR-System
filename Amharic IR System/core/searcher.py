from .tokenizer import AmharicTokenizer
from .tfidf import TFIDFCalculator
import math
from collections import defaultdict

class AmharicSearcher:
    """Search engine for Amharic documents"""
    
    def __init__(self, index):
        self.index = index
        self.tokenizer = AmharicTokenizer()
        self.tfidf_calculator = TFIDFCalculator()
    
    def search(self, query, top_k=10, search_type="tfidf"):
        """Search for documents matching the query"""
        query = query.strip()
        if not query:
            return []
        
        # If query is very short (1-2 characters), use character search
        if len(query) <= 2:
            return self.character_search(query, top_k)
        
        # Try different search methods
        results = []
        
        # First try TF-IDF search
        results = self.tfidf_search(query, top_k)
        
        # If no results, try partial matching
        if not results:
            results = self.partial_match_search(query, top_k)
        
        # If still no results, try character-based search
        if not results:
            results = self.character_search(query, top_k)
        
        return results
    
    def tfidf_search(self, query, top_k=10):
        """Search using TF-IDF ranking"""
        query_terms = self.tokenizer.tokenize(query, stem=True)
        
        if not query_terms:
            return []
        
        # Calculate TF-IDF scores
        scores = defaultdict(float)
        
        for term in query_terms:
            if term in self.index.inverted_index:
                for doc_id, term_info in self.index.inverted_index[term].items():
                    scores[doc_id] += term_info.get('tf_idf', 0)
        
        # Rank documents
        ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Prepare results
        results = []
        for doc_id, score in ranked_docs[:top_k]:
            doc_info = self.index.get_document(doc_id)
            if not doc_info:
                continue
                
            snippet = self._generate_snippet(doc_info['content'], query_terms)
            
            results.append({
                'doc_id': doc_id,
                'title': doc_id,
                'score': score,
                'snippet': snippet,
                'full_content': doc_info['content'][:300] + "..." if len(doc_info['content']) > 300 else doc_info['content'],
                'filepath': doc_info.get('filepath', ''),
                'metadata': doc_info.get('metadata', {}),
                'length': doc_info.get('length', 0)
            })
        
        return results
    
    def partial_match_search(self, query, top_k=10):
        """Search for partial matches in terms"""
        query = query.lower()
        results = []
        
        for doc_id, doc_info in self.index.documents.items():
            # Check if query appears in document content
            content_lower = doc_info['content'].lower()
            if query in content_lower:
                # Find position
                pos = content_lower.find(query)
                
                # Create snippet
                snippet = self._create_snippet_from_position(doc_info['content'], pos, len(query))
                
                # Calculate relevance score based on frequency
                score = content_lower.count(query) / len(doc_info['content']) * 100
                
                results.append({
                    'doc_id': doc_id,
                    'title': doc_id,
                    'score': score,
                    'snippet': snippet,
                    'full_content': doc_info['content'][:300] + "..." if len(doc_info['content']) > 300 else doc_info['content'],
                    'filepath': doc_info.get('filepath', ''),
                    'metadata': doc_info.get('metadata', {}),
                    'length': doc_info.get('length', 0)
                })
                
                if len(results) >= top_k:
                    break
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def character_search(self, query, top_k=10):
        """Search for character sequences"""
        query = query.lower()
        results = []
        
        for doc_id, doc_info in self.index.documents.items():
            content_lower = doc_info['content'].lower()
            
            # Count occurrences
            count = content_lower.count(query)
            if count > 0:
                # Find first position
                pos = content_lower.find(query)
                
                # Create snippet
                snippet = self._create_snippet_from_position(doc_info['content'], pos, len(query))
                
                # Calculate score based on frequency
                score = (count * len(query)) / len(doc_info['content']) * 100
                
                results.append({
                    'doc_id': doc_id,
                    'title': doc_id,
                    'score': score,
                    'snippet': snippet,
                    'full_content': doc_info['content'][:300] + "..." if len(doc_info['content']) > 300 else doc_info['content'],
                    'filepath': doc_info.get('filepath', ''),
                    'metadata': doc_info.get('metadata', {}),
                    'length': doc_info.get('length', 0)
                })
                
                if len(results) >= top_k:
                    break
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def _generate_snippet(self, content, query_terms):
        """Generate a text snippet showing query terms in context"""
        # Simple snippet generation
        words = content.split()
        
        if len(words) <= 40:
            return content
        
        # Find first occurrence of any query term
        for i, word in enumerate(words):
            if i >= len(words) - 10:
                break
                
            # Clean the word for comparison
            clean_word = word.strip('.,!?;:"\'፡።፣').lower()
            for term in query_terms:
                if term.lower() in clean_word or clean_word in term.lower():
                    start = max(0, i - 10)
                    end = min(len(words), i + 30)
                    snippet_words = words[start:end]
                    
                    # Add ellipsis
                    if start > 0:
                        snippet_words = ['...'] + snippet_words
                    if end < len(words):
                        snippet_words = snippet_words + ['...']
                    
                    return ' '.join(snippet_words)
        
        # If no query term found, return beginning
        return ' '.join(words[:40]) + '...'
    
    def _create_snippet_from_position(self, content, position, query_length):
        """Create snippet from specific position"""
        if position < 0:
            # Query not found
            return content[:100] + "..." if len(content) > 100 else content
        
        start = max(0, position - 50)
        end = min(len(content), position + query_length + 100)
        
        snippet = content[start:end]
        
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        
        return snippet
    
    def get_search_stats(self, query):
        """Get statistics about search query"""
        query_terms = self.tokenizer.tokenize(query, stem=True)
        
        stats = {
            'query': query,
            'query_terms': query_terms,
            'term_stats': []
        }
        
        for term in query_terms:
            if term in self.index.doc_frequencies:
                df = self.index.doc_frequencies[term]
                idf = math.log((self.index.total_docs + 1) / (df + 1)) + 1
                stats['term_stats'].append({
                    'term': term,
                    'document_frequency': df,
                    'idf': idf
                })
        
        return stats