import uvicorn

uvicorn.run("monitor360:app", host="0.0.0.0", port=8000, reload=True)
