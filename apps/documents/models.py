from django.db import models
import json

class Document(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    file = models.FileField(upload_to='documents/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-uploaded_at']

class InvertedIndex(models.Model):
    term = models.CharField(max_length=100, db_index=True)
    document_frequency = models.IntegerField(default=0)
    postings = models.TextField()  # Almacena JSON con {doc_id: tf}
    
    def get_postings(self):
        return json.loads(self.postings)
    
    def set_postings(self, postings_dict):
        self.postings = json.dumps(postings_dict)
    
    def __str__(self):
        return f"{self.term} (df: {self.document_frequency})"

class SearchQuery(models.Model):
    query_text = models.TextField()
    query_type = models.CharField(max_length=10, choices=[
        ('BOOLEAN', 'Boolean'),
        ('VECTOR', 'Vectorial'),
    ])
    results_count = models.IntegerField(default=0)
    searched_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.query_text} - {self.searched_at}"