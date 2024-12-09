from fastapi import FastAPI
from app.database.database import Base, engine
from app.services.connection_manager import ConnectionManager
from app.sokcets_handlers import client_ws, solver_ws
from app.database.events import init_events

# Create database tables
Base.metadata.create_all(bind=engine)

init_events()


app = FastAPI()



# @app.on_event("startup")
# async def startup_event():
#     logger.info("Starting up FastAPI application")
#     # You can add additional initialization here if needed

# @app.on_event("shutdown")
# async def shutdown_event():
#     logger.info("Shutting down FastAPI application")


# Register WebSocket routes
app.add_api_websocket_route("/ws/client/{client_id}", client_ws.client_websocket)
app.add_api_websocket_route("/ws/solver/{solver_id}", solver_ws.solver_websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)