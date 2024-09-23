from app.main import app


if __name__ == '__main__':
    import uvicorn
    
    PORT = os.environ.get('PORT') or 8080
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
