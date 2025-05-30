# app/main.py
from fastapi import FastAPI
import pandas as pd
from pydantic import BaseModel

app = FastAPI()

# Mock de dados (poderia ser um banco de dados real)
df = pd.DataFrame({
    "id": [1, 2, 3],
    "nome": ["Alice", "Bob", "Charlie"],
    "vendas": [100, 200, 150]
})

@app.get("/dados")
def get_dados():
    return df.to_dict(orient="records")

@app.get("/dados/{id}")
def get_dado(id: int):
    return df[df["id"] == id].to_dict(orient="records")