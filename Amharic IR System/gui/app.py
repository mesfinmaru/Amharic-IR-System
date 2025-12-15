import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import os
import sys
from collections import defaultdict

# Import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.indexer import InvertedIndex
from core.searcher import AmharicSearcher
from core.tfidf import TFIDFCalculator

class AmharicIRGUI:
    """GUI for Amharic Information Retrieval System"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("አማርኛ መረጃ መፈለጊያ ስርዓት - Amharic Information Retrieval System")
        
        # Get the base directory (where the application is running from)
        if getattr(sys, 'frozen', False):
            # If running as exe/pyinstaller bundle
            self.base_dir = os.path.dirname(sys.executable)
        else:
            # If running as script
            self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Initialize IR system
        self.index = InvertedIndex()
        self.searcher = None
        self.current_results = []
        
        # Status
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        # Create GUI
        self.create_widgets()
        
        # Try to auto-detect documents folder
        self.auto_detect_documents()
    
    def auto_detect_documents(self):
        """Auto-detect documents folder relative to application"""
        # Check for documents in standard locations
        possible_paths = [
            os.path.join(self.base_dir, "data", "documents"),  # Main location
            os.path.join(self.base_dir, "documents"),           # Alternative
            os.path.join(self.base_dir, "data"),                # Another alternative
            os.path.join(os.getcwd(), "data", "documents"),     # Current working directory
            os.path.join(os.getcwd(), "documents")              # CWD alternative
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                # Check if it has .txt files
                try:
                    files = os.listdir(path)
                    txt_files = [f for f in files if f.lower().endswith('.txt')]
                    if txt_files:
                        self.doc_dir_var.set(path)
                        print(f"Auto-detected documents folder: {path}")
                        return True
                except:
                    continue
        
        # If no documents found, use default relative path
        default_path = os.path.join(self.base_dir, "data", "documents")
        self.doc_dir_var.set(default_path)
        return False
    
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Create main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#2c3e50')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(
            header_frame,
            text="አማርኛ መረጃ መፈለጊያ ስርዓት - Amharic Information Retrieval System",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#2c3e50',
            padx=20,
            pady=10
        )
        title_label.pack()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Search
        search_frame = tk.Frame(notebook)
        notebook.add(search_frame, text="🔍 Search")
        self.create_search_tab(search_frame)
        
        # Tab 2: Index Management
        index_frame = tk.Frame(notebook)
        notebook.add(index_frame, text="📁 Index")
        self.create_index_tab(index_frame)
        
        # Tab 3: Statistics
        stats_frame = tk.Frame(notebook)
        notebook.add(stats_frame, text="📊 Statistics")
        self.create_stats_tab(stats_frame)
        
        # Tab 4: Document Viewer
        viewer_frame = tk.Frame(notebook)
        notebook.add(viewer_frame, text="📄 Document Viewer")
        self.create_viewer_tab(viewer_frame)
        
        # Status bar
        status_bar = tk.Frame(main_frame, bg='#2c3e50', height=25)
        status_bar.pack(fill=tk.X, pady=(5, 0))
        
        status_label = tk.Label(
            status_bar,
            textvariable=self.status_var,
            font=('Arial', 9),
            fg='white',
            bg='#2c3e50',
            padx=10
        )
        status_label.pack(side=tk.LEFT)
        
        # Add document count
        self.doc_count_var = tk.StringVar(value="Documents: 0")
        doc_count_label = tk.Label(
            status_bar,
            textvariable=self.doc_count_var,
            font=('Arial', 9),
            fg='white',
            bg='#2c3e50',
            padx=10
        )
        doc_count_label.pack(side=tk.RIGHT)
    
    def create_search_tab(self, parent):
        """Create search tab"""
        # Search box
        search_container = tk.Frame(parent)
        search_container.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            search_container,
            text="Search Query:",
            font=('Arial', 12, 'bold')
        ).pack(anchor=tk.W)
        
        self.search_entry = tk.Entry(
            search_container,
            font=('Arial', 14),
            width=50
        )
        self.search_entry.pack(fill=tk.X, pady=(5, 10))
        self.search_entry.bind('<Return>', lambda e: self.perform_search())
        
        # Search button
        search_btn = tk.Button(
            search_container,
            text="Search (TF-IDF)",
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            command=self.perform_search,
            padx=30,
            pady=5
        )
        search_btn.pack(pady=(5, 20))
        
        # Results area
        results_frame = tk.Frame(parent)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Results label
        self.results_label = tk.Label(
            results_frame,
            text="Results will appear here",
            font=('Arial', 11)
        )
        self.results_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Results text widget with scrollbar
        results_container = tk.Frame(results_frame)
        results_container.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = scrolledtext.ScrolledText(
            results_container,
            wrap=tk.WORD,
            font=('Arial', 10),
            height=20
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Clear results button
        clear_btn = tk.Button(
            results_frame,
            text="Clear Results",
            command=self.clear_results,
            bg='#e74c3c',
            fg='white',
            padx=10,
            pady=2
        )
        clear_btn.pack(anchor=tk.E, pady=(5, 0))
    
    def create_index_tab(self, parent):
        """Create index management tab"""
        # Index operations frame
        ops_frame = tk.Frame(parent)
        ops_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Load documents section
        tk.Label(
            ops_frame,
            text="Load Documents:",
            font=('Arial', 12, 'bold')
        ).pack(anchor=tk.W, pady=(0, 10))
        
        load_frame = tk.Frame(ops_frame)
        load_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.doc_dir_var = tk.StringVar()
        # Set to default path - will be updated by auto_detect_documents
        default_path = os.path.join(self.base_dir, "data", "documents")
        self.doc_dir_var.set(default_path)
        
        dir_entry = tk.Entry(
            load_frame,
            textvariable=self.doc_dir_var,
            font=('Arial', 10),
            width=40
        )
        dir_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        browse_btn = tk.Button(
            load_frame,
            text="Browse",
            command=self.browse_doc_dir,
            padx=10
        )
        browse_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        load_btn = tk.Button(
            load_frame,
            text="Load & Index",
            command=self.load_and_index,
            bg='#27ae60',
            fg='white',
            padx=15,
            pady=3
        )
        load_btn.pack(side=tk.LEFT)
        
        # Auto-detect button
        auto_detect_btn = tk.Button(
            load_frame,
            text="Auto-Detect",
            command=self.auto_detect_documents,
            bg='#f39c12',
            fg='white',
            padx=10,
            pady=3
        )
        auto_detect_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Save/Load index section
        tk.Label(
            ops_frame,
            text="Save/Load Index:",
            font=('Arial', 12, 'bold')
        ).pack(anchor=tk.W, pady=(0, 10))
        
        index_ops_frame = tk.Frame(ops_frame)
        index_ops_frame.pack(fill=tk.X, pady=(0, 20))
        
        save_btn = tk.Button(
            index_ops_frame,
            text="Save Index",
            command=self.save_index,
            bg='#3498db',
            fg='white',
            padx=15,
            pady=3
        )
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        load_index_btn = tk.Button(
            index_ops_frame,
            text="Load Index",
            command=self.load_index,
            bg='#9b59b6',
            fg='white',
            padx=15,
            pady=3
        )
        load_index_btn.pack(side=tk.LEFT)
        
        # Index statistics
        tk.Label(
            ops_frame,
            text="Index Information:",
            font=('Arial', 12, 'bold')
        ).pack(anchor=tk.W, pady=(20, 10))
        
        # Text widget for index info
        self.index_info_text = scrolledtext.ScrolledText(
            ops_frame,
            wrap=tk.WORD,
            font=('Arial', 9),
            height=10
        )
        self.index_info_text.pack(fill=tk.X, pady=(0, 10))
        
        # Refresh button
        refresh_btn = tk.Button(
            ops_frame,
            text="Refresh Statistics",
            command=self.refresh_index_info,
            padx=10,
            pady=2
        )
        refresh_btn.pack(anchor=tk.E)
    
    def create_stats_tab(self, parent):
        """Create statistics tab"""
        # Term statistics section
        term_frame = tk.Frame(parent)
        term_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(
            term_frame,
            text="Term Statistics:",
            font=('Arial', 12, 'bold')
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Term search
        search_term_frame = tk.Frame(term_frame)
        search_term_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            search_term_frame,
            text="Term:"
        ).pack(side=tk.LEFT)
        
        self.term_entry = tk.Entry(
            search_term_frame,
            font=('Arial', 11),
            width=20
        )
        self.term_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        term_search_btn = tk.Button(
            search_term_frame,
            text="Get Statistics",
            command=self.get_term_stats,
            bg='#3498db',
            fg='white',
            padx=10
        )
        term_search_btn.pack(side=tk.LEFT)
        
        # Term statistics display
        self.term_stats_text = scrolledtext.ScrolledText(
            term_frame,
            wrap=tk.WORD,
            font=('Courier', 9),
            height=15
        )
        self.term_stats_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Top terms section
        tk.Label(
            term_frame,
            text="Top 10 Most Frequent Terms:",
            font=('Arial', 12, 'bold')
        ).pack(anchor=tk.W, pady=(10, 5))
        
        self.top_terms_text = scrolledtext.ScrolledText(
            term_frame,
            wrap=tk.WORD,
            font=('Courier', 9),
            height=8
        )
        self.top_terms_text.pack(fill=tk.BOTH, expand=True)
    
    def create_viewer_tab(self, parent):
        """Create document viewer tab"""
        viewer_frame = tk.Frame(parent)
        viewer_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(
            viewer_frame,
            text="Document Viewer:",
            font=('Arial', 12, 'bold')
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Document selection
        select_frame = tk.Frame(viewer_frame)
        select_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            select_frame,
            text="Select Document:"
        ).pack(side=tk.LEFT)
        
        self.doc_listbox = tk.Listbox(
            select_frame,
            height=5,
            width=30
        )
        self.doc_listbox.pack(side=tk.LEFT, padx=(5, 10))
        
        view_btn = tk.Button(
            select_frame,
            text="View Document",
            command=self.view_document,
            bg='#3498db',
            fg='white',
            padx=10
        )
        view_btn.pack(side=tk.LEFT)
        
        # Document content display
        self.doc_content_text = scrolledtext.ScrolledText(
            viewer_frame,
            wrap=tk.WORD,
            font=('Arial', 10),
            height=20
        )
        self.doc_content_text.pack(fill=tk.BOTH, expand=True)
    
    def browse_doc_dir(self):
        """Browse for documents directory"""
        # Start from the base directory
        initial_dir = self.base_dir
        
        directory = filedialog.askdirectory(
            title="Select Folder Containing Amharic Text Files",
            initialdir=initial_dir,
            mustexist=True
        )
        if directory:
            self.doc_dir_var.set(directory)
    
    def load_and_index(self):
        """Load and index documents"""
        def index_thread():
            self.status_var.set("Indexing documents...")
            self.root.update()
            
            directory = self.doc_dir_var.get().strip()
            
            if not directory:
                messagebox.showwarning("Warning", "Please select a folder first")
                self.status_var.set("Ready")
                return
            
            # Check if directory exists
            if not os.path.exists(directory):
                # Try to create it
                try:
                    os.makedirs(directory, exist_ok=True)
                    messagebox.showinfo("Info", 
                        f"Created directory: {directory}\n"
                        f"Please place your Amharic .txt files in this folder and try again.")
                    self.status_var.set("Ready")
                    return
                except Exception as e:
                    messagebox.showerror("Error", f"Cannot access directory: {directory}\nError: {e}")
                    self.status_var.set("Ready")
                    return
            
            # Check for .txt files
            try:
                files = os.listdir(directory)
                txt_files = [f for f in files if f.lower().endswith('.txt')]
                
                if not txt_files:
                    messagebox.showwarning("Warning", 
                        f"No .txt files found in: {directory}\n"
                        f"Please add Amharic text files (.txt extension) to the folder.")
                    self.status_var.set("Ready")
                    return
                    
                # Show what files will be indexed
                file_list = "\n".join(txt_files[:10])  # Show first 10
                if len(txt_files) > 10:
                    file_list += f"\n... and {len(txt_files) - 10} more files"
                
                response = messagebox.askyesno("Confirm Indexing", 
                    f"Found {len(txt_files)} .txt files in:\n{directory}\n\n"
                    f"Files to index:\n{file_list}\n\n"
                    f"Continue with indexing?")
                
                if not response:
                    self.status_var.set("Ready")
                    return
                    
            except Exception as e:
                messagebox.showerror("Error", f"Cannot read directory: {directory}\nError: {e}")
                self.status_var.set("Ready")
                return
            
            # Index documents
            stats = self.index.index_directory(directory)
            
            # Calculate TF-IDF
            if self.index.total_docs > 0:
                TFIDFCalculator.calculate_tf_idf(
                    self.index.inverted_index,
                    self.index.doc_frequencies,
                    self.index.total_docs,
                    self.index.doc_lengths
                )
                self.searcher = AmharicSearcher(self.index)
            
            # Update UI
            self.doc_count_var.set(f"Documents: {self.index.total_docs}")
            self.refresh_index_info()
            self.update_doc_list()
            
            # Show results
            if stats['successful'] > 0:
                messagebox.showinfo("Success", 
                    f"Successfully indexed {stats['successful']} Amharic documents.\n"
                    f"Failed: {stats['failed']}\n\n"
                    f"You can now search in the 'Search' tab!")
            else:
                messagebox.showwarning("Warning", 
                    f"No documents were indexed.\n"
                    f"Make sure your .txt files contain Amharic text (UTF-8 encoded).")
            
            self.status_var.set("Ready")
        
        # Run in thread to keep UI responsive
        threading.Thread(target=index_thread, daemon=True).start()
    
    def perform_search(self):
        """Perform search operation"""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query in Amharic")
            return
        
        if not self.searcher:
            messagebox.showwarning("Warning", "Please index documents first (go to Index tab)")
            return
        
        self.status_var.set(f"Searching for: {query}")
        self.root.update()
        
        # Perform search
        results = self.searcher.search(query, top_k=20)
        self.current_results = results
        
        # Display results
        self.results_text.delete(1.0, tk.END)
        
        if not results:
            self.results_text.insert(tk.END, f"No results found for: '{query}'\n\n")
            self.results_label.config(text=f"No results found for: '{query}'")
        else:
            self.results_label.config(text=f"Found {len(results)} results for: '{query}'")
            
            for i, result in enumerate(results, 1):
                self.results_text.insert(tk.END, f"Result #{i}\n")
                self.results_text.insert(tk.END, f"{'='*60}\n")
                self.results_text.insert(tk.END, f"Document: {result['title']}\n")
                self.results_text.insert(tk.END, f"TF-IDF Score: {result['score']:.4f}\n")
                self.results_text.insert(tk.END, f"Length: {result['length']} terms\n")
                self.results_text.insert(tk.END, f"Snippet: {result['snippet']}\n")
                self.results_text.insert(tk.END, f"{'='*60}\n\n")
        
        self.status_var.set("Ready")
    
    def clear_results(self):
        """Clear search results"""
        self.results_text.delete(1.0, tk.END)
        self.results_label.config(text="Results will appear here")
        self.current_results = []
    
    def save_index(self):
        """Save index to file"""
        if self.index.total_docs == 0:
            messagebox.showwarning("Warning", "No documents indexed to save")
            return
            
        # Default save location is in the base directory
        default_filename = os.path.join(self.base_dir, "amharic_index.json")
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Index File",
            initialfile="amharic_index.json",
            initialdir=self.base_dir
        )
        if filepath:
            if self.index.save_index(filepath):
                messagebox.showinfo("Success", f"Index saved to:\n{os.path.basename(filepath)}")
            else:
                messagebox.showerror("Error", "Failed to save index")
    
    def load_index(self):
        """Load index from file"""
        # Start from base directory
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Index File",
            initialdir=self.base_dir
        )
        if filepath:
            if self.index.load_index(filepath):
                # Calculate TF-IDF
                if self.index.total_docs > 0:
                    TFIDFCalculator.calculate_tf_idf(
                        self.index.inverted_index,
                        self.index.doc_frequencies,
                        self.index.total_docs,
                        self.index.doc_lengths
                    )
                    self.searcher = AmharicSearcher(self.index)
                
                # Update UI
                self.doc_count_var.set(f"Documents: {self.index.total_docs}")
                self.refresh_index_info()
                self.update_doc_list()
                
                messagebox.showinfo("Success", f"Loaded index with {self.index.total_docs} documents")
            else:
                messagebox.showerror("Error", "Failed to load index")
    
    def refresh_index_info(self):
        """Refresh index statistics display"""
        self.index_info_text.delete(1.0, tk.END)
        
        if self.index.total_docs == 0:
            self.index_info_text.insert(tk.END, "No documents indexed yet.\n\n")
            self.index_info_text.insert(tk.END, "To index documents:\n")
            self.index_info_text.insert(tk.END, "1. Make sure you have Amharic .txt files\n")
            self.index_info_text.insert(tk.END, "2. Click 'Auto-Detect' to find them\n")
            self.index_info_text.insert(tk.END, "3. Or click 'Browse' to select folder\n")
            self.index_info_text.insert(tk.END, "4. Click 'Load & Index' button\n")
            return
        
        stats = self.index.get_index_stats()
        
        self.index_info_text.insert(tk.END, "INDEX STATISTICS\n")
        self.index_info_text.insert(tk.END, "="*50 + "\n")
        self.index_info_text.insert(tk.END, f"Total Documents: {stats['total_documents']}\n")
        self.index_info_text.insert(tk.END, f"Total Unique Terms: {stats['total_unique_terms']}\n")
        self.index_info_text.insert(tk.END, f"Total Terms: {stats['total_terms']}\n")
        self.index_info_text.insert(tk.END, f"Average Document Length: {stats['average_document_length']:.1f} terms\n")
        self.index_info_text.insert(tk.END, "\n")
        
        # Update top terms in separate text widget
        self.top_terms_text.delete(1.0, tk.END)
        if stats['most_frequent_terms']:
            self.top_terms_text.insert(tk.END, "Rank  Term          Frequency\n")
            self.top_terms_text.insert(tk.END, "-"*30 + "\n")
            for i, (term, freq) in enumerate(stats['most_frequent_terms'], 1):
                self.top_terms_text.insert(tk.END, f"{i:2d}.  {term:15} {freq}\n")
    
    def get_term_stats(self):
        """Get statistics for a specific term"""
        term = self.term_entry.get().strip()
        if not term:
            messagebox.showwarning("Warning", "Please enter an Amharic term")
            return
        
        if self.index.total_docs == 0:
            messagebox.showwarning("Warning", "Please index documents first")
            return
        
        term_info = self.index.get_term_info(term)
        
        self.term_stats_text.delete(1.0, tk.END)
        
        if not term_info:
            self.term_stats_text.insert(tk.END, f"Term '{term}' not found in index.")
            return
        
        df = term_info['document_frequency']
        idf = 0
        if df > 0:
            import math
            idf = math.log((self.index.total_docs + 1) / (df + 1)) + 1
        
        self.term_stats_text.insert(tk.END, f"TERM STATISTICS: '{term}'\n")
        self.term_stats_text.insert(tk.END, "="*50 + "\n")
        self.term_stats_text.insert(tk.END, f"Document Frequency (DF): {df}\n")
        self.term_stats_text.insert(tk.END, f"IDF: {idf:.4f}\n")
        self.term_stats_text.insert(tk.END, f"Appears in {len(term_info['documents'])} documents\n")
        
        if term_info['documents']:
            self.term_stats_text.insert(tk.END, "\nDocument Details:\n")
            self.term_stats_text.insert(tk.END, "-"*50 + "\n")
            
            for doc_id, info in list(term_info['documents'].items())[:10]:  # Show first 10
                self.term_stats_text.insert(tk.END, f"\nDocument: {doc_id}\n")
                self.term_stats_text.insert(tk.END, f"  Term Frequency (TF): {info['tf']}\n")
                self.term_stats_text.insert(tk.END, f"  TF-IDF Score: {info.get('tf_idf', 0):.6f}\n")
                positions = info['positions'][:10]  # Show first 10 positions
                pos_str = ', '.join(map(str, positions))
                if len(info['positions']) > 10:
                    pos_str += f", ... (+{len(info['positions']) - 10} more)"
                self.term_stats_text.insert(tk.END, f"  Positions: {pos_str}\n")
    
    def update_doc_list(self):
        """Update document list in viewer"""
        self.doc_listbox.delete(0, tk.END)
        
        for doc_id in sorted(self.index.documents.keys()):
            self.doc_listbox.insert(tk.END, doc_id)
    
    def view_document(self):
        """View selected document"""
        selection = self.doc_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a document")
            return
        
        doc_id = self.doc_listbox.get(selection[0])
        doc_info = self.index.get_document(doc_id)
        
        if not doc_info:
            messagebox.showerror("Error", f"Document {doc_id} not found")
            return
        
        self.doc_content_text.delete(1.0, tk.END)
        
        # Display document info
        self.doc_content_text.insert(tk.END, f"DOCUMENT: {doc_id}\n")
        self.doc_content_text.insert(tk.END, "="*60 + "\n\n")
        
        # Display metadata
        metadata = doc_info.get('metadata', {})
        if metadata:
            self.doc_content_text.insert(tk.END, "Metadata:\n")
            for key, value in metadata.items():
                if key == 'filename':
                    self.doc_content_text.insert(tk.END, f"  File: {value}\n")
                elif key == 'size':
                    self.doc_content_text.insert(tk.END, f"  Size: {value} bytes\n")
                elif key == 'filepath':
                    self.doc_content_text.insert(tk.END, f"  Path: {value}\n")
            self.doc_content_text.insert(tk.END, "\n")
        
        # Display document length
        self.doc_content_text.insert(tk.END, f"Document Length: {doc_info.get('length', 0)} terms\n\n")
        
        # Display full content
        self.doc_content_text.insert(tk.END, "Content:\n")
        self.doc_content_text.insert(tk.END, "-"*40 + "\n")
        self.doc_content_text.insert(tk.END, doc_info['content'])