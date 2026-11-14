from fastapi import FastAPI

app = FastAPI(
    title="Sales and Inventory Management System",
    version="1.0.0"
)


@app.get("/")
def home():
    return {"message": "Sales and Inventory API is running"}