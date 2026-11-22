from fastapi import FastAPI

app = FastAPI(
    title="MNEMIA API",
    description="Backend API για αναζήτηση μνημείων μέσω Europeana",
    version="0.1.0",
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "MNEMIA FastAPI"}