import os
from flask import Flask, jsonify

app = Flask(__name__)

API_NAME = os.getenv("API_NAME", "api")
API_BEHAVIOR = os.getenv("API_BEHAVIOR", "ok")  # "ok" ou "broken"


@app.get("/")
def root():
  if API_BEHAVIOR == "broken":
    return "erro", 500

  return "ok", 200


@app.get("/status")
def status():
  # Mantém um endpoint adicional, mas sem expor detalhes de arquitetura.
  if API_BEHAVIOR == "broken":
    return jsonify({"resultado": "erro"}), 500

  return jsonify({"resultado": "ok"}), 200


if __name__ == "__main__":
  # Flask por padrão escuta em 127.0.0.1; precisamos em 0.0.0.0 para o Docker
  app.run(host="0.0.0.0", port=5000)

