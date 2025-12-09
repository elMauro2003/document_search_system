from django.urls import path
from apps.documents.views import *

urlpatterns = [
    path('', index, name='index'),
    path('upload/', upload_document, name='upload'),
    path('search/', search, name='search'),
    path('inverted-index/', inverted_index_view, name='inverted_index'),
    path('document/<int:doc_id>/', document_detail, name='document_detail'),
    path('stats/', get_index_stats, name='get_stats'),
    path('clear-index/', clear_index, name='clear_index'),
]