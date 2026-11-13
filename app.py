from fastapi import FastAPI

app = FastAPI(title="MODURA OpenCMO System")

@app.get("/")
def read_root():
    return {"status": "success", "message": "MODURA OpenCMO is live and running!"}
