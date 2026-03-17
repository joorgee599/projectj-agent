# Ejemplos de Uso - API de Chat

## ✅ Endpoints Disponibles

### 1. Chat Estándar (Respuesta completa)
**POST** `/chat`

#### Primera interacción (sin thread_id)
```json
{
  "message": "Hola, ¿qué productos tienes disponibles?"
}
```

**Respuesta:**
```json
{
  "response": "¡Hola! Soy el Agente ProjectJ...",
  "thread_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
}
```

#### Interacciones siguientes (con thread_id para mantener contexto)
```json
{
  "message": "¿Cuál me recomiendas?",
  "thread_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
}
```

---

### 2. Chat con Streaming (Respuesta en tiempo real)
**POST** `/chat/stream`

#### Request
```json
{
  "message": "Muéstrame todos los productos disponibles",
  "thread_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
}
```

#### Respuesta (Server-Sent Events)
```
data: {"type": "tool_start", "data": "list_products", "thread_id": "..."}

data: {"type": "content", "data": "Tengo", "thread_id": "..."}

data: {"type": "content", "data": " los", "thread_id": "..."}

data: {"type": "content", "data": " siguientes", "thread_id": "..."}

...

data: {"type": "end", "thread_id": "..."}
```

---

## 🔧 Validaciones

### Mensaje
- **Mínimo:** 1 carácter
- **Máximo:** 2000 caracteres

### Thread ID
- **Formato:** UUID v4 (ej: `a1b2c3d4-e5f6-7890-1234-567890abcdef`)
- **Opcional:** Si no se proporciona, se crea automáticamente

---

## 💻 Ejemplos con cURL

### Chat estándar (primera vez)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola, ¿qué productos tienes?"}'
```

### Chat con contexto
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Cuál es el más barato?",
    "thread_id": "TU-THREAD-ID-AQUI"
  }'
```

### Chat con streaming
```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -N \
  -d '{"message": "Dame detalles de todos los productos"}'
```

---

## 🌐 Ejemplos con JavaScript/TypeScript

### Fetch API (React/Next.js)

#### Chat estándar
```typescript
const chatStandard = async (message: string, threadId?: string) => {
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, thread_id: threadId })
  });
  
  const data = await response.json();
  return data; // { response: "...", thread_id: "..." }
};
```

#### Chat con streaming
```typescript
const chatStream = async (message: string, threadId?: string) => {
  const response = await fetch('http://localhost:8000/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, thread_id: threadId })
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader!.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        
        if (data.type === 'content') {
          console.log(data.data); // Mostrar cada chunk
        } else if (data.type === 'tool_start') {
          console.log(`Usando herramienta: ${data.data}`);
        } else if (data.type === 'end') {
          console.log('Stream completado');
        }
      }
    }
  }
};
```

---

## 📝 Manejo de Sesiones

### Flujo recomendado:

1. **Primera interacción:** No enviar `thread_id`
2. **Guardar el `thread_id`** recibido en la respuesta
3. **Siguientes mensajes:** Enviar el mismo `thread_id` para mantener contexto
4. **Nueva conversación:** Omitir `thread_id` para generar uno nuevo

### Ejemplo de flujo:
```typescript
// Primera pregunta
const response1 = await chatStandard("Hola");
const threadId = response1.thread_id; // Guardar para futuras interacciones

// Segunda pregunta (con contexto)
const response2 = await chatStandard("¿Cuáles son los precios?", threadId);

// Tercera pregunta (mantiene todo el contexto anterior)
const response3 = await chatStandard("Dame el más barato", threadId);
```

---

## ⚠️ Manejo de Errores

### Error 400 - Validación
```json
{
  "detail": "String should have at most 2000 characters"
}
```

### Error 500 - Error del servidor
```json
{
  "detail": "Error interno del servidor"
}
```

### Recomendación:
Siempre usar try-catch y manejar los errores apropiadamente en el frontend.

---

## 📊 Logging

Todos los eventos se registran en los logs del servidor:
- Creación de sesiones
- Procesamiento de mensajes
- Errores

Para ver los logs en tiempo real:
```bash
uvicorn main:app --reload --log-level info
```
