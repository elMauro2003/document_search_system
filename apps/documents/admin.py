from django.contrib import admin
from apps.documents.models import Document, InvertedIndex, SearchQuery

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploaded_at', 'processed']
    list_filter = ['processed', 'uploaded_at']
    search_fields = ['title', 'content']

@admin.register(InvertedIndex)
class InvertedIndexAdmin(admin.ModelAdmin):
    list_display = ['term', 'document_frequency']
    search_fields = ['term']

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['query_text', 'query_type', 'results_count', 'searched_at']
    list_filter = ['query_type', 'searched_at']
    search_fields = ['query_text']