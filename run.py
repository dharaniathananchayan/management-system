import uvicorn
import os

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    print(f"Starting Learning Progress & Assessment Management System server at http://{host}:{port}")
    print(f"Swagger Documentation available at http://{host}:{port}/docs")
    print(f"Interactive UI Dashboard available at http://{host}:{port}/")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
