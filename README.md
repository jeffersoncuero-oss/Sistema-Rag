Sistema RAG Multimodal V2
Sistema de recuperación aumentada por generación (RAG) que permite
cargar documentos, indexar su contenido, recuperar fragmentos relevantes
y generar respuestas mediante modelos de lenguaje.

Esta versión conserva la interfaz Streamlit, sus componentes visuales y
los servicios RAG del proyecto original. Incorpora FastAPI como backend
independiente, al que Streamlit envía consultas y documentos mediante
HTTP.
1. Arquitectura
  Servicio                Tecnología              Responsabilidad
  app                   Streamlit               Interfaz para cargar
documentos y realizar
consultas.

  backend               FastAPI / Uvicorn       API para recibir
documentos y procesar
consultas RAG.

  chroma                ChromaDB                Almacenamiento de
fragmentos y
representaciones
vectoriales.

  ollama                Ollama                  Ejecución de modelos de
lenguaje y embeddings.
ollama-init           Ollama                  Descarga de los modelos
configurados.
Flujo general
1. El usuario interactúa con Streamlit.
2. Streamlit envía solicitudes HTTP al backend FastAPI.
3. FastAPI recibe documentos o preguntas.
4. El procesador documental extrae el contenido y lo divide en
   fragmentos.
5. Ollama genera los embeddings.
6. ChromaDB almacena los fragmentos y sus representaciones vectoriales.
7. El servicio RAG recupera fragmentos relevantes mediante búsqueda
   híbrida.
8. Los fragmentos recuperados se envían al modelo de lenguaje como
   contexto.
9. FastAPI devuelve la respuesta y las fuentes a Streamlit.
2. Tecnologías
- Python 3.11
- Streamlit
- FastAPI y Uvicorn
- ChromaDB
- Ollama
- OpenAI Python SDK
- Requests
- PyMuPDF
- python-docx
- Docker y Docker Compose
- Pytest y HTTPX
3. Estructura del proyecto
Sistema-Rag-V/
├── api/
│   └── main.py
├── components/
│   ├── api_client.py
│   ├── query_tab.py
│   └── upload_tab.py
├── services/
│   ├── rag_service.py
│   ├── document_processor.py
│   ├── chroma_client.py
│   └── ollama_client.py
├── tests/
│   └── test_api.py
├── app.py
├── Dockerfile
├── docker-compose.yml
├── docker-compose-local.yml
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── .env.example
├── .gitignore
├── .dockerignore
├── README.md
├── test_busqueda_hibrida.py
├── test_busqueda_textual.py
├── test_document.py
├── test_rag.py
├── test_rag_directo.py
└── test_retrieval.py
La estructura muestra los archivos principales; pueden existir otros
archivos auxiliares o de configuración.
4. Requisitos previos
- Docker Desktop instalado y en ejecución.
- Docker Compose disponible mediante docker compose.
- Git para clonar el repositorio.
- Conexión a Internet para descargar imágenes y modelos.
- Python 3.11 para ejecutar las pruebas localmente.
5. Obtener y configurar el proyecto
5.1. Clonar el repositorio
Cuando el repositorio remoto esté publicado:
git clone URL_DEL_REPOSITORIO
cd Sistema-Rag-V
Reemplaza URL_DEL_REPOSITORIO por la dirección real del repositorio
Git.
5.2. Crear el archivo de entorno
Desde la carpeta raíz:
Copy-Item .env.example .env
Revisa .env.example y completa en .env los valores que correspondan
al entorno. No publiques .env: puede contener información sensible.
Comparte únicamente la plantilla .env.example.
6. Inicialización completa con Docker Compose
El archivo de orquestación utilizado por el proyecto es
docker-compose.yml.
6.1. Verificar Docker
docker --version
docker compose version
Asegúrate de que Docker Desktop esté iniciado.
6.2. Construir las imágenes
Desde la raíz del proyecto:
docker compose -f docker-compose.yml build
6.3. Iniciar todos los servicios
docker compose -f docker-compose.yml up -d
Se iniciarán los servicios definidos en Compose:
1. chroma: base de datos vectorial.
2. ollama: servicio de modelos.
3. ollama-init: descarga de los modelos configurados.
4. backend: API FastAPI.
5. app: interfaz Streamlit.
No es necesario iniciar Uvicorn manualmente: el servicio backend ya
tiene configurado su comando de arranque en Docker Compose.
6.4. Verificar el estado
docker compose -f docker-compose.yml ps
Los servicios deben alcanzar el estado saludable cuando tengan
configurado un healthcheck. ollama-init puede finalizar con estado
Exited (0) después de completar correctamente la descarga de modelos;
es un servicio de inicialización y no un servidor permanente.
6.5. Revisar los registros
docker logs sistema-rag-backend --tail 50
docker logs sistema-rag-app --tail 50
docker logs sistema-rag-ollama --tail 50
En los registros del backend se esperan mensajes equivalentes a:
Application startup complete.
Uvicorn running on http://0.0.0.0:8001
6.6. Puertos y direcciones
  Servicio      Puerto interno   Puerto local
  Streamlit               8501           8502
FastAPI                 8001           8002
ChromaDB                8000           8001
Ollama                 11434          11435

Direcciones locales:

  Servicio             Dirección
  Streamlit            http://localhost:8502
FastAPI              http://localhost:8002
Swagger              http://localhost:8002/docs
Estado del backend   http://localhost:8002/health
ChromaDB             http://localhost:8001
Ollama               http://localhost:11435

Dentro de Docker, los servicios se comunican mediante sus nombres DNS y
puertos internos:
- Backend: http://backend:8001
- ChromaDB: http://chroma:8000
- Ollama: http://ollama:11434
No sustituyas estos puertos internos por los puertos publicados en
Windows al configurar la comunicación entre contenedores.
7. Inicialización de FastAPI desde cero
Esta sección describe cómo poner en marcha y verificar el backend en un
equipo nuevo.
7.1. Ubicarse en la raíz
cd Sistema-Rag-V
7.2. Configurar el entorno
Si todavía no existe .env:
Copy-Item .env.example .env
Completa los valores necesarios según la plantilla y la configuración
del proyecto.
7.3. Construir la imagen del backend
La configuración actual utiliza la misma imagen para los servicios
backend y app:
docker compose -f docker-compose.yml build backend
7.4. Iniciar los servicios necesarios
Para una instalación nueva, inicia toda la arquitectura:
docker compose -f docker-compose.yml up -d
Esto permite que FastAPI encuentre los servicios auxiliares configurados
en la red Docker, especialmente ChromaDB y Ollama. ollama-init
descarga los modelos definidos en la configuración.
7.5. Comprobar el backend
docker compose -f docker-compose.yml ps
docker logs sistema-rag-backend --tail 50
Consultar el endpoint de salud desde PowerShell:
Invoke-RestMethod http://localhost:8002/health
Respuesta esperada:
{
  "status": "ok",
  "service": "rag-backend"
}
7.6. Abrir Swagger
En el navegador:

http://localhost:8002/docs

Desde Swagger se pueden consultar los endpoints y enviar solicitudes de
prueba.
7.7. Detener y volver a iniciar
Detener los servicios sin eliminar los volúmenes:
docker compose -f docker-compose.yml stop
Iniciarlos nuevamente:
docker compose -f docker-compose.yml start
Estos comandos detienen o inician los contenedores existentes. No
eliminan los volúmenes de datos.
8. API REST
El backend está desarrollado con FastAPI y expone los siguientes
endpoints:
GET /health
Verifica que el proceso de la API esté disponible.

Respuesta:
{
  "status": "ok",
  "service": "rag-backend"
}
GET /documents/count
Consulta la cantidad de fragmentos almacenados en ChromaDB. Si no puede
consultar el almacenamiento, la API devuelve HTTP 503.
POST /documents/upload
Recibe e indexa documentos en los formatos permitidos:
- PDF
- DOCX
- TXT
- MD
La API valida la extensión, que el archivo no esté vacío y que no supere
el límite configurado mediante MAX_FILE_SIZE_MB (por defecto, 50 MB).
POST /query
Realiza una consulta sobre los documentos indexados.
  Parámetro                           Descripción
  question                          Pregunta obligatoria, entre 1 y
10.000 caracteres.

  top_k                             Cantidad de fragmentos solicitados.
Valor predeterminado: 3; rango: 1 a
20.
history                           Historial opcional de mensajes con
roles user o assistant.
La respuesta contiene answer y sources.

Documentación interactiva: http://localhost:8002/docs
9. Pruebas automatizadas
Las pruebas automatizadas están en tests/ y utilizan Pytest junto con
el cliente de pruebas de FastAPI.
9.1. Instalar dependencias de desarrollo
Con Python 3.11 instalado:
python -m pip install -r requirements-dev.txt
9.2. Ejecutar las pruebas
Desde la raíz:
python -m pytest -v
El archivo pytest.ini configura tests/ como ubicación de las pruebas
automatizadas. Así Pytest no ejecuta automáticamente los scripts
manuales test_*.py conservados en la raíz.
9.3. Cobertura actual
Las siete pruebas implementadas verifican:
- Estado del backend.
- Consulta de cantidad de fragmentos.
- Procesamiento de consultas RAG mediante un servicio simulado.
- Rechazo de preguntas vacías.
- Rechazo de extensiones no permitidas.
- Rechazo de archivos vacíos.
- Carga documental mediante un procesador simulado.
Resultado obtenido durante la validación local:
7 passed in 1.68s
Las pruebas utilizan servicios simulados para no insertar ni borrar
documentos en la instancia real de ChromaDB y para no depender de Ollama
durante su ejecución. Validan el comportamiento de los endpoints, pero
no sustituyen pruebas de integración completas con los servicios reales.
9.4. Scripts manuales conservados
El proyecto también conserva estos scripts en la raíz:
- test_busqueda_hibrida.py
- test_busqueda_textual.py
- test_document.py
- test_rag.py
- test_rag_directo.py
- test_retrieval.py
Sirven para exploraciones y comprobaciones manuales. Algunos acceden
directamente a ChromaDB, Ollama o archivos de prueba; revisa sus rutas y
efectos antes de ejecutarlos en un entorno con datos importantes.
10. Decisiones técnicas
- Se conserva la interfaz Streamlit del proyecto original.
- Se incorpora FastAPI como backend independiente.
- Streamlit consume el backend mediante solicitudes HTTP.
- Se reutilizan los servicios existentes de procesamiento documental y
  RAG.
- ChromaDB se utiliza como almacenamiento vectorial.
- Ollama proporciona los modelos de embeddings y generación.
- Docker Compose coordina los componentes.
- Pytest permite validar endpoints con servicios simulados, sin
  intervenir en el almacenamiento real durante las pruebas
  automatizadas.
11. Consideraciones operativas
- Los servicios auxiliares deben estar disponibles para realizar
  consultas RAG.
- Los modelos requeridos deben descargarse y estar disponibles en
  Ollama.
- Los documentos deben indexarse antes de realizar consultas sobre su
  contenido.
- La disponibilidad de /health confirma que el backend responde; no
  garantiza por sí sola que ChromaDB y Ollama estén operativos.
- Mantén credenciales y configuraciones sensibles en .env; no
  publiques ese archivo.
- Conserva los volúmenes de Docker cuando quieras mantener los
  documentos y datos persistidos.
12. Control de versiones
El proyecto utiliza Git para registrar cambios y mantener un historial
de desarrollo.

Se recomienda utilizar commits semánticos:

  Prefijo      Uso
  feat       Nuevas funcionalidades.
fix        Correcciones.
test       Pruebas.
docs       Documentación.
refactor   Reorganización interna.
chore      Mantenimiento y configuración.

Ejemplos:
git commit -m "feat: add FastAPI backend"
git commit -m "test: add automated API tests"
git commit -m "docs: document V2 architecture and setup"
Los mensajes son ejemplos de convención; el historial debe reflejar los
cambios reales del proyecto.