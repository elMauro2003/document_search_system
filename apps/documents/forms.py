from django import forms
from .models import Document

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file', 'content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'O ingrese el contenido del documento directamente aquí...'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del documento'
            }),
        }

class SearchForm(forms.Form):
    QUERY_TYPES = [
        ('BOOLEAN', 'Búsqueda Booleana'),
        ('VECTOR', 'Búsqueda Vectorial'),
    ]
    
    query = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: machine AND learning OR "artificial intelligence"',
            'hx-post': '/search/',
            'hx-trigger': 'keyup changed delay:500ms',
            'hx-target': '#search-results',
            'hx-indicator': '.htmx-indicator'
        })
    )
    
    query_type = forms.ChoiceField(
        choices=QUERY_TYPES,
        initial='BOOLEAN',
        widget=forms.Select(attrs={'class': 'form-select'})
    )