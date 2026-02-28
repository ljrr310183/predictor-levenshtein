# Project Mandate: Predictor Levenshtein

## 1. Technical Stack
- **Language**: Python 3.14
- **Framework**: Puro (Websockets, asyncio)
- **Database**: Memoria (Lista/Diccionario en Python)
- **Librería Core**: `levenshtein` (o `rapidfuzz`)

## 2. Architecture Principles
- **Separación de Responsabilidades**: Lógica de cálculo (Levensthein/Bigramas) separada del transporte (Websockets).
- **Rendimiento**: Carga del diccionario pre-procesado en memoria al inicio para no penalizar el bucle de eventos asíncronos. Buscar O(1) siempre que sea posible.
- **Enfoque Híbrido**: 
  - *Mid-word*: Autocompletado vía similitud ortográfica (Levenshtein).
  - *End-of-word (Espacio)*: Predicción de siguiente palabra vía relaciones probabilísticas pre-computadas (N-Gram/Bigramas).

## 3. Business Context
- Construcción de un predictor de palabras (autocompletado + sugerencia de siguiente palabra) en tiempo real, enviando fragmentos vía websocket y recibiendo las palabras más exactas/probables del diccionario.

## Reglas Estrictas No Negociables
1. **No hacer más de lo que se pide**: Limitarse estrictamente a lo reportado/solicitado. El usuario está construyendo la lógica manual y conceptualmente; el agente NO debe generar código que implemente o "adelante" funcionalidad a menos que el usuario lo solicite explícitamente.
