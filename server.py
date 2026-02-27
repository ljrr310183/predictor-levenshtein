import asyncio
from websockets.asyncio.server import serve
import json
from predictor import get_best_matches

async def message_manager(websocket):
    print("Conexion iniciada")

    try:
        async for mensaje in websocket:
            try:
                print(f"Mensaje recibido: {mensaje}")
                #get matches
                matches = get_best_matches(mensaje)
                
                print(f"Buscando coincidencias para: {mensaje}")
                predictions = json.dumps({"predictions": matches})

                await websocket.send(predictions)
                print("Respuesta enviada!")
            except Exception as e:
                print(f"Error procesando mensaje: {e}")
    finally:
        print("Conexion cerrada")


async def main():
    print("Server websocket started in http://localhost:8765 ...")

    async with serve(message_manager, "localhost", 8765) as server:
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())