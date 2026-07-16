from fastapi import FastAPI

from backend.app import config

app = FastAPI(
    title=config.APP_NAME,
    debug=config.DEBUG,
)


@app.get("/")
def root():
    return {"message": "DataLens Agent is running."}


@app.get("/health")
def health():
    return {"status": "ok"}
