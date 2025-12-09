import numpy as np
import math
import re
import json
from collections import defaultdict, Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk

# Descargar recursos de NLTK si es necesario
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords')

class DocumentIndexer:
    def __init__(self):
        self.inverted_index = {}
        self.documents = {}
        self.doc_vectors = {}
        self.term_idf = {}
        self.vectorizer = None
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
    def preprocess_text(self, text):
        """Preprocesa el texto: tokeniza, elimina stopwords y aplica stemming"""
        # Convertir a minúsculas
        text = text.lower()
        
        # Eliminar caracteres especiales (excepto operadores booleanos)
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Tokenizar
        tokens = word_tokenize(text)
        
        # Eliminar stopwords y aplicar stemming
        processed_tokens = []
        for token in tokens:
            if token not in self.stop_words and len(token) > 2:
                stemmed = self.stemmer.stem(token)
                processed_tokens.append(stemmed)
        
        return processed_tokens
    
    def build_inverted_index(self, documents):
        """Construye el índice invertido a partir de los documentos"""
        self.inverted_index = defaultdict(dict)
        self.documents = {doc_id: doc for doc_id, doc in enumerate(documents)}
        
        for doc_id, doc in enumerate(documents):
            tokens = self.preprocess_text(doc)
            term_freq = Counter(tokens)
            
            for term, freq in term_freq.items():
                self.inverted_index[term][doc_id] = freq
        
        # Calcular frecuencias de documento
        self.calculate_idf()
        
        return self.inverted_index
    
    def calculate_idf(self):
        """Calcula IDF para cada término"""
        total_docs = len(self.documents)
        for term, postings in self.inverted_index.items():
            df = len(postings)
            self.term_idf[term] = math.log(total_docs / (df + 1)) + 1
    
    def calculate_tf_idf(self):
        """Calcula vectores TF-IDF para todos los documentos"""
        self.doc_vectors = {}
        
        for doc_id, doc in self.documents.items():
            vector = {}
            tokens = self.preprocess_text(doc)
            term_freq = Counter(tokens)
            
            for term, tf in term_freq.items():
                if term in self.term_idf:
                    # TF normalizado
                    tf_norm = tf / len(tokens)
                    # TF-IDF
                    vector[term] = tf_norm * self.term_idf[term]
            
            self.doc_vectors[doc_id] = vector
        
        return self.doc_vectors
    
    def boolean_search(self, query):
        """Realiza búsqueda booleana (AND, OR)"""
        # Parsear la consulta booleana
        query = query.lower()
        
        # Dividir en términos y operadores
        tokens = re.findall(r'(\bAND\b|\bOR\b|\(|\)|\w+)', query)
        
        # Evaluar la expresión booleana
        result_set = self.evaluate_boolean_expression(tokens)
        
        # Calcular similitud para ordenar resultados
        results = []
        for doc_id in result_set:
            if doc_id in self.doc_vectors:
                similarity = self.cosine_similarity(query, doc_id)
                results.append((doc_id, similarity))
        
        # Ordenar por similitud
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
    
    def evaluate_boolean_expression(self, tokens):
        """Evalúa una expresión booleana"""
        stack = []
        operator_stack = []
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token == '(':
                operator_stack.append(token)
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    self.apply_operator(stack, operator_stack.pop())
                operator_stack.pop()  # Eliminar '('
            elif token.upper() in ['AND', 'OR']:
                while (operator_stack and 
                       operator_stack[-1] in ['AND', 'OR'] and
                       self.precedence(operator_stack[-1]) >= self.precedence(token)):
                    self.apply_operator(stack, operator_stack.pop())
                operator_stack.append(token.upper())
            else:
                # Es un término de búsqueda
                term_set = set(self.get_documents_for_term(token))
                stack.append(term_set)
            
            i += 1
        
        # Aplicar operadores restantes
        while operator_stack:
            self.apply_operator(stack, operator_stack.pop())
        
        return stack[0] if stack else set()
    
    def get_documents_for_term(self, term):
        """Obtiene documentos que contienen un término"""
        processed_term = self.preprocess_text(term)
        if processed_term and processed_term[0] in self.inverted_index:
            return list(self.inverted_index[processed_term[0]].keys())
        return []
    
    def apply_operator(self, stack, operator):
        """Aplica un operador booleano"""
        if len(stack) < 2:
            return
        
        b = stack.pop()
        a = stack.pop()
        
        if operator == 'AND':
            stack.append(a.intersection(b))
        elif operator == 'OR':
            stack.append(a.union(b))
    
    def precedence(self, operator):
        """Define precedencia de operadores"""
        if operator == 'AND':
            return 2
        elif operator == 'OR':
            return 1
        return 0
    
    def vector_search(self, query):
        """Realiza búsqueda vectorial"""
        query_tokens = self.preprocess_text(query)
        query_vector = {}
        
        # Construir vector de consulta
        term_freq = Counter(query_tokens)
        for term, tf in term_freq.items():
            if term in self.term_idf:
                query_vector[term] = tf * self.term_idf[term]
        
        # Calcular similitud con cada documento
        results = []
        for doc_id, doc_vector in self.doc_vectors.items():
            similarity = self.cosine_similarity_vectors(query_vector, doc_vector)
            if similarity > 0:
                results.append((doc_id, similarity))
        
        # Ordenar por similitud
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
    
    def cosine_similarity(self, query, doc_id):
        """Calcula similitud coseno entre consulta y documento"""
        query_vector = {}
        query_tokens = self.preprocess_text(query)
        term_freq = Counter(query_tokens)
        
        for term, tf in term_freq.items():
            if term in self.term_idf:
                query_vector[term] = tf * self.term_idf[term]
        
        doc_vector = self.doc_vectors.get(doc_id, {})
        
        return self.cosine_similarity_vectors(query_vector, doc_vector)
    
    def cosine_similarity_vectors(self, vec1, vec2):
        """Calcula similitud coseno entre dos vectores"""
        # Obtener todos los términos únicos
        terms = set(vec1.keys()).union(set(vec2.keys()))
        
        if not terms:
            return 0
        
        # Convertir a arrays
        v1 = np.array([vec1.get(term, 0) for term in terms])
        v2 = np.array([vec2.get(term, 0) for term in terms])
        
        # Calcular producto punto y normas
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        return dot_product / (norm1 * norm2)
    
    def get_index_statistics(self):
        """Obtiene estadísticas del índice"""
        total_terms = len(self.inverted_index)
        total_docs = len(self.documents)
        avg_terms_per_doc = sum(len(self.preprocess_text(doc)) 
                               for doc in self.documents.values()) / total_docs if total_docs > 0 else 0
        
        return {
            'total_terms': total_terms,
            'total_documents': total_docs,
            'avg_terms_per_document': avg_terms_per_doc,
        }