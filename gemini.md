# Project Mandate: Predictor Levenshtein

## 1. Technical Stack
- **Language**: Python 3.14
- **Framework**: Puro (Websockets, asyncio)
- **Database**: Memoria (Lista/Diccionario en Python)
- **Librería Core**: `levenshtein` (o `rapidfuzz`)

## 2. Architecture Principles
- **Separación de Responsabilidades**: Lógica de cálculo (Levensthein) separada del transporte (Websockets).
- **Rendimiento**: Carga del diccionario en memoria al inicio para no penalizar el bucle de eventos asíncronos.

## 3. Business Context
- Construcción de un predictor de palabras (autocompletado/sugerencia ortográfica) en tiempo real, enviando fragmentos vía websocket y recibiendo las palabras más cercanas del diccionario.
