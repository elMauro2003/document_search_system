from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from apps.documents.models import Document, InvertedIndex, SearchQuery
from apps.documents.forms import DocumentUploadForm, SearchForm
from utils.indexer import DocumentIndexer
import json

# Instancia global del indexador
indexer = DocumentIndexer()
documents_loaded = False

def load_documents_from_db():
    """Carga documentos desde la base de datos"""
    global indexer, documents_loaded
    
    if not documents_loaded:
        docs = Document.objects.filter(processed=True)
        doc_contents = [doc.content for doc in docs]
        
        if doc_contents:
            indexer.build_inverted_index(doc_contents)
            indexer.calculate_tf_idf()
            documents_loaded = True

def index(request):
    """Página principal"""
    load_documents_from_db()
    
    stats = indexer.get_index_statistics()
    recent_searches = SearchQuery.objects.all().order_by('-searched_at')[:5]
    
    context = {
        'stats': stats,
        'recent_searches': recent_searches,
        'form': SearchForm(),
    }
    
    return render(request, 'documents/index.html', context)

def upload_document(request):
    """Subir nuevo documento"""
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            
            # Si se subió un archivo, leer su contenido
            if document.file:
                try:
                    # Para archivos de texto simple
                    if document.file.name.endswith('.txt'):
                        document.content = document.file.read().decode('utf-8')
                    # Para otros tipos, solo guardar el nombre
                    else:
                        document.content = f"Contenido del archivo: {document.file.name}"
                except:
                    document.content = f"Contenido del archivo: {document.file.name}"
            
            document.processed = True
            document.save()
            
            # Actualizar el índice
            global indexer, documents_loaded
            docs = Document.objects.filter(processed=True)
            doc_contents = [doc.content for doc in docs]
            
            indexer.build_inverted_index(doc_contents)
            indexer.calculate_tf_idf()
            documents_loaded = True
            
            messages.success(request, 'Documento subido y procesado exitosamente.')
            return redirect('index')
    else:
        form = DocumentUploadForm()
    
    return render(request, 'documents/upload.html', {'form': form})

def search(request):
    """Realizar búsqueda"""
    load_documents_from_db()
    
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            query_type = form.cleaned_data['query_type']
            
            # Guardar la consulta en el historial
            SearchQuery.objects.create(
                query_text=query,
                query_type=query_type,
                results_count=0  # Se actualizará después
            )
            
            # Realizar la búsqueda
            if query_type == 'BOOLEAN':
                results = indexer.boolean_search(query)
            else:
                results = indexer.vector_search(query)
            
            # Convertir resultados a documentos
            doc_results = []
            for doc_id, similarity in results[:50]:  # Limitar a 50 resultados
                docs = Document.objects.filter(processed=True)
                if doc_id < len(docs):
                    doc = docs[doc_id]
                    doc_results.append({
                        'document': doc,
                        'similarity': round(similarity * 100, 2),
                        'doc_id': doc_id,
                    })
            
            # Actualizar conteo de resultados
            SearchQuery.objects.filter(
                query_text=query,
                query_type=query_type
            ).update(results_count=len(doc_results))
            
            context = {
                'results': doc_results,
                'query': query,
                'query_type': query_type,
                'results_count': len(doc_results),
            }
            
            if request.headers.get('HX-Request'):
                return render(request, 'documents/results_partial.html', context)
            
            return render(request, 'documents/search.html', context)
    
    # Si es GET, mostrar formulario vacío
    form = SearchForm()
    return render(request, 'documents/search.html', {'form': form})

def inverted_index_view(request):
    """Mostrar índice invertido"""
    load_documents_from_db()
    
    # Obtener términos para paginación
    terms = list(indexer.inverted_index.keys())
    terms.sort()
    
    paginator = Paginator(terms, 50)  # 50 términos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Preparar datos para mostrar
    index_data = []
    for term in page_obj.object_list:
        postings = indexer.inverted_index.get(term, {})
        df = len(postings)
        idf = indexer.term_idf.get(term, 0)
        
        index_data.append({
            'term': term,
            'document_frequency': df,
            'inverse_document_frequency': round(idf, 4),
            'postings': postings,
        })
    
    context = {
        'index_data': index_data,
        'page_obj': page_obj,
        'total_terms': len(terms),
    }
    
    return render(request, 'documents/inverted_index.html', context)

def document_detail(request, doc_id):
    """Ver detalle de documento"""
    load_documents_from_db()
    
    docs = Document.objects.filter(processed=True)
    if doc_id < len(docs):
        document = docs[doc_id]
        
        # Obtener términos importantes del documento
        if doc_id in indexer.doc_vectors:
            doc_vector = indexer.doc_vectors[doc_id]
            top_terms = sorted(doc_vector.items(), key=lambda x: x[1], reverse=True)[:10]
        else:
            top_terms = []
        
        context = {
            'document': document,
            'doc_id': doc_id,
            'top_terms': top_terms,
        }
        
        return render(request, 'documents/document_detail.html', context)
    
    messages.error(request, 'Documento no encontrado.')
    return redirect('index')

def get_index_stats(request):
    """Obtener estadísticas del índice (para HTMX)"""
    load_documents_from_db()
    
    stats = indexer.get_index_statistics()
    
    return JsonResponse(stats)

def clear_index(request):
    """Limpiar índice (para desarrollo)"""
    global indexer, documents_loaded
    
    indexer = DocumentIndexer()
    documents_loaded = False
    
    messages.success(request, 'Índice limpiado exitosamente.')
    return redirect('index')