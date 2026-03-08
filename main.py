# main.py
# Local development entry point.
# Run: python main.py

from api.index import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.index:app", host="0.0.0.0", port=8000, reload=True)