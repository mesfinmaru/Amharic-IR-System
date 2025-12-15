from .tokenizer import AmharicTokenizer
from collections import defaultdict
import os
import json

class InvertedIndex:
    """Inverted index for Amharic documents"""
    
    def __init__(self):
        self.tokenizer = AmharicTokenizer()
        self.inverted_index = defaultdict(lambda: defaultdict(list))
        self.documents = {}
        self.doc_frequencies = defaultdict(int)
        self.doc_lengths = {}
        self.total_docs = 0
    
    def index_document(self, doc_id, content, filepath=None, metadata=None):
        """Index a single document"""
        try:
            # Tokenize with positions
            tokens_with_pos = self.tokenizer.tokenize_with_positions(content, stem=True)
            tokens = [token for token, _ in tokens_with_pos]
            
            # Store document
            self.documents[doc_id] = {
                'content': content,
                'tokens': tokens,
                'filepath': filepath,
                'length': len(tokens),
                'metadata': metadata or {}
            }
            
            # Track term positions
            term_positions = defaultdict(list)
            for token, pos in tokens_with_pos:
                term_positions[token].append(pos)
            
            # Calculate term frequencies (TF)
            term_freq = {}
            for token in tokens:
                term_freq[token] = term_freq.get(token, 0) + 1
            
            # Update inverted index
            for term, positions in term_positions.items():
                self.inverted_index[term][doc_id] = {
                    'tf': term_freq[term],
                    'positions': positions,
                    'tf_idf': 0.0
                }
            
            # Update document frequencies (DF)
            for term in set(tokens):
                self.doc_frequencies[term] += 1
            
            self.doc_lengths[doc_id] = len(tokens)
            self.total_docs += 1
            
            return True
            
        except Exception as e:
            print(f"Error indexing document {doc_id}: {e}")
            return False
    
    def index_directory(self, directory_path, file_extension='.txt'):
        """Index all documents in a directory"""
        stats = {
            'successful': 0,
            'failed': 0,
            'files': []
        }
        
        if not os.path.exists(directory_path):
            print(f"Directory {directory_path} does not exist!")
            return stats
        
        for filename in os.listdir(directory_path):
            if filename.endswith(file_extension):
                file_path = os.path.join(directory_path, filename)
                doc_id = os.path.splitext(filename)[0]
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    metadata = {
                        'filename': filename,
                        'filepath': file_path,
                        'size': os.path.getsize(file_path)
                    }
                    
                    if self.index_document(doc_id, content, file_path, metadata):
                        stats['successful'] += 1
                        stats['files'].append({
                            'filename': filename,
                            'status': 'success'
                        })
                        print(f"Indexed: {filename}")
                    else:
                        stats['failed'] += 1
                        stats['files'].append({
                            'filename': filename,
                            'status': 'failed'
                        })
                        
                except Exception as e:
                    stats['failed'] += 1
                    stats['files'].append({
                        'filename': filename,
                        'status': 'error',
                        'error': str(e)
                    })
                    print(f"Error reading {filename}: {e}")
        
        return stats
    
    def get_document(self, doc_id):
        """Get document by ID"""
        return self.documents.get(doc_id)
    
    def get_term_info(self, term):
        """Get information about a term"""
        if term not in self.inverted_index:
            return None
        
        return {
            'term': term,
            'document_frequency': self.doc_frequencies[term],
            'documents': self.inverted_index[term]
        }
    
    def get_index_stats(self):
        """Get index statistics"""
        total_terms = sum(self.doc_lengths.values())
        avg_doc_length = total_terms / self.total_docs if self.total_docs > 0 else 0
        
        # Get top 10 most frequent terms
        most_frequent = sorted(
            self.doc_frequencies.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'total_documents': self.total_docs,
            'total_unique_terms': len(self.inverted_index),
            'total_terms': total_terms,
            'average_document_length': avg_doc_length,
            'most_frequent_terms': most_frequent
        }
    
    def save_index(self, filepath):
        """Save index to JSON file"""
        try:
            # Convert defaultdict to regular dict for JSON serialization
            inverted_index_dict = {}
            for term, doc_dict in self.inverted_index.items():
                inverted_index_dict[term] = dict(doc_dict)
            
            index_data = {
                'inverted_index': inverted_index_dict,
                'doc_frequencies': dict(self.doc_frequencies),
                'doc_lengths': self.doc_lengths,
                'total_docs': self.total_docs,
                'documents': self.documents
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
            
            print(f"Index saved to {filepath}")
            return True
            
        except Exception as e:
            print(f"Error saving index: {e}")
            return False
    
    def load_index(self, filepath):
        """Load index from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            # Reconstruct defaultdicts
            self.inverted_index = defaultdict(lambda: defaultdict(list))
            for term, doc_dict in index_data['inverted_index'].items():
                self.inverted_index[term] = doc_dict
            
            self.doc_frequencies = defaultdict(int, index_data['doc_frequencies'])
            self.doc_lengths = index_data['doc_lengths']
            self.total_docs = index_data['total_docs']
            self.documents = index_data['documents']
            
            print(f"Index loaded from {filepath}")
            return True
            
        except Exception as e:
            print(f"Error loading index: {e}")
            return False