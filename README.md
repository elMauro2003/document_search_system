------------
![](https://github.com/elMauro2003/imagenes/blob/main/document_search_system.png)

# Sistema de Indexación y Búsqueda de Documentos

Aplicación web desarrollada en [Django](https://www.djangoproject.com/ "Django") que implementa técnicas avanzadas de recuperación de información. El sistema utiliza el modelo vectorial con ponderación TF-IDF y permite búsquedas booleanas (AND, OR) sobre documentos de texto.

## Características Principales:
✅ Indexación automática con preprocesamiento NLP

✅ Búsqueda booleana con operadores AND/OR y paréntesis

✅ Búsqueda vectorial por similitud coseno

✅ Índice invertido navegable

✅ Interfaz con Bootstrap 5

✅ Reactividad en tiempo real con HTMX

✅ Visualización de vectores TF-IDF

✅ Historial de búsquedas


---

## Requisitos Previos

- **Python**: Versión 3.8 o superior instalada en tu sistema.
- **Pip**: Administrador de paquetes de Python (incluido con Python).
- **Conexión a Internet**: Para instalar las dependencias necesarias.

---

## Descargar el repositorio

```
git clone https://github.com/elMauro2003/document_search_system.git
      
```

## Configuración del Entorno

### 1. Crear un Entorno Virtual
1. Abre una terminal o línea de comandos.
2. Navega al directorio donde se encuentra el archivo `manage.py`.
3. Ejecuta el siguiente comando para crear un entorno virtual:
```
python -m venv env
```

### 2. Ejecutar el Entorno Virtual
Linux Run env
```
source env/bin/activate
```

Windows Run env
```
env\Scripts\activate
```

## 3. Instalar los requirements del proyecto

```
pip install -r requirements.txt
```

## 4 Correr las migraciones

```python
python manage.py migrate
```

## Uso del Software


### 🔧 Funcionalidades Técnicas

- **🏗️ Proceso de Indexación**
    Documento → Tokenización → Stopwords → Stemming → Conteo TF → Cálculo IDF → Vector TF-IDF → Índice Invertido

	### Ejemplo práctico:
	```"El aprendizaje automático es fascinante"```

	 ### Procesamiento:
	 ```
	Minúsculas: "el aprendizaje automático es fascinante"
	Tokenización: ["el", "aprendizaje", "automático", "es", "fascinante"]
	Stopwords: ["aprendizaje", "automático", "fascinante"]
	Stemming: ["aprend", "automat", "fascin"]
	TF: {"aprend":1, "automat":1, "fascin":1}
	```

- **🔍 Tipos de Búsqueda**
	#### A. Búsqueda Booleana
	```
	# Sintaxis válida:
	• "python AND django"
	• "machine OR learning"
	• "(python OR java) AND web"
	• "data AND (science OR analysis)"
	```

	### Cómo funciona: 
	```
	# Consulta: "python AND django"
	1. Parse: ["python", "AND", "django"]
	2. Conjuntos: docs_python ∩ docs_django
	3. Resultado: Documentos que contienen AMBOS términos
	```

	### B. Búsqueda Vectorial
	```
	# Consulta: "machine learning python"
	1. Vector consulta: {"machin":1, "learn":1, "python":1}
	2. Similaridad coseno con cada documento
	3. Ranking por porcentaje de similitud
	```


- **📐 Cálculo TF-IDF**
	### Fórmulas implementadas:
	```
	TF(term, doc) = frecuencia(term en doc) / total_términos(doc)
	IDF(term) = log(N / (1 + df(term))) + 1
	TF-IDF = TF × IDF
	```

	```
	# Término "python" en 10 documentos totales
	df("python") = 2  # Aparece en 2 documentos
	IDF = log(10 / (1+2)) + 1 = 1.2039

	# En documento A: frecuencia=3, total términos=100
	TF = 3/100 = 0.03
	TF-IDF = 0.03 × 1.2039 = 0.0361
	```

## 🧪 Casos de Prueba Recomendados

### 📚 Conjunto de Datos de Prueba
**Documento 1 - Inteligencia Artificial**

**Título:** Fundamentos de IA
> La inteligencia artificial es la simulación de procesos de inteligencia humana por máquinas, especialmente sistemas informáticos. Las aplicaciones específicas de la IA incluyen sistemas expertos, procesamiento de lenguaje natural y visión por computadora.**

------------

**Documento 2 - Machine Learning**

**Título:** Aprendizaje Automático
> El aprendizaje automático es un campo de la inteligencia artificial que permite a los sistemas aprender y mejorar automáticamente de la experiencia sin ser programados explícitamente. Se centra en el desarrollo de programas que pueden acceder a datos y aprender de ellos.**


------------

**Documento 3 - Python para Ciencia de Datos**

**Título:** Python en Ciencia de Datos
> Python es un lenguaje de programación ampliamente utilizado en ciencia de datos, aprendizaje automático y aplicaciones web. Bibliotecas populares incluyen NumPy, Pandas, Scikit-learn y TensorFlow para implementar algoritmos de machine learning.


### 🔍 Consultas para Probar
1 . Búsqueda Booleana Básica
- Encuentra documentos con ambos términos
```"inteligencia AND artificial"```

- Encuentra documentos con cualquiera de los términos
```"python OR aprendizaje"```

- Combinación compleja
```"(machine AND learning) OR (ciencia AND datos)"```

2 . Búsqueda Vectorial
- Ranking por relevancia
```"máquinas aprendizaje sistemas"```

- Términos específicos
```"numpy pandas scikit tensorflow"```

- Consultas naturales
```"¿Cómo funciona el aprendizaje automático?"```

3 . Pruebas de Stemming
-- Debería encontrar todas las formas

```"aprender"        -- encuentra "aprendizaje", "aprende", etc.```

```"programa"        -- encuentra "programación", "programado"```

```"máquina"         -- encuentra "máquinas"```


###  📊 Resultados Esperados
**Para consulta:  ```"python AND aprendizaje"```**

📄 Python en Ciencia de Datos [92%]
**Contiene:** ```"python"``` y ```"aprendizaje"``` (stemmed)

📄 Aprendizaje Automático [85%]
**Contiene:** ```"aprendizaje"``` pero no ```"python"```


## ⚙️ Configuración y Personalización
### 🔧 Archivo de Configuración ```(settings.py)```

	# Límites del sistema
	MAX_DOCUMENTS = 1000      # Máximo de documentos
	MAX_TERMS = 10000         # Máximo de términos únicos

	# Preprocesamiento
	STOPWORDS_LANGUAGE = 'english'  # Cambiar a 'spanish' para español
	STEM_LANGUAGE = 'english'       # Stemmer a usar

### 🌐 Cambiar Idioma a Español

1. Instalar stopwords en español:
	```
	import nltk
	nltk.download('stopwords')
	```

2. Modificar indexer.py:
	```
	self.stop_words = set(stopwords.words('spanish'))
	```
3. Cambiar configuración Django:
	```
	# settings.py
	LANGUAGE_CODE = 'es-es'
	TIME_ZONE = 'America/Mexico_City'
	```


------------



Mauricio J. Avalo Tamayo © 2025 All Rights Reserved
