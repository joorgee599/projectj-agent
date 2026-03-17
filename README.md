# ProjectJ - Agente de Productos

Agente conversacional creado en Python que ayuda a gestionar temas relacionados con productos.
Aplicación diseñada para gestionar inventario y carrito de compras, compatible con plataformas móviles y web.

## 🚀 Características

- ✅ **Chat con contexto**: Mantiene el historial de conversación por sesión
- ✅ **Streaming en tiempo real**: Respuestas progresivas para mejor UX
- ✅ **Validaciones robustas**: Validación de entrada con Pydantic
- ✅ **Logging completo**: Trazabilidad de todas las operaciones
- ✅ **Manejo de errores**: Respuestas claras ante problemas
- ✅ **Integración con LangChain**: Usando GPT-4o-mini y LangGraph

## 📋 Requisitos

- Python 3.9+
- OpenAI API Key
- FastAPI
- LangChain

## 🔧 Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
# Crear archivo .env con:
OPENAI_API_KEY=tu-api-key-aqui
```

## 🏃 Ejecución

```bash
# Modo desarrollo
uvicorn main:app --reload --port 8000

# Producción
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📡 Endpoints

### `POST /chat`
Chat estándar con respuesta completa

### `POST /chat/stream`
Chat con streaming (Server-Sent Events)

### `GET /hello`
Health check

Ver [API_EXAMPLES.md](API_EXAMPLES.md) para ejemplos detallados de uso.

## 🏗️ Arquitectura

```
projectj-agente/
├── main.py                 # Punto de entrada FastAPI
├── app/
│   ├── agents/
│   │   ├── agent/         # Definición del agente LangGraph
│   │   ├── services/      # Lógica de negocio del chat
│   │   └── tools/         # Herramientas del agente
│   ├── config/            # Configuración
│   ├── routers/           # Endpoints de la API
│   └── schemas/           # Modelos Pydantic
└── requirements.txt
```

## 🔄 Mejoras Implementadas

- **Gestión de sesiones mejorada**: Thread ID para mantener contexto entre mensajes
- **Streaming**: Respuestas progresivas en tiempo real
- **Validaciones**: Límites en mensajes y formato de IDs
- **Logging**: Trazabilidad completa de operaciones
- **Manejo de errores**: Respuestas HTTP apropiadas

## 📚 Próximos pasos

- [ ] Persistencia con PostgreSQL/Redis
- [ ] Rate limiting
- [ ] Métricas y observabilidad
- [ ] Autenticación de usuarios
- [ ] Caché de respuestas frecuentes