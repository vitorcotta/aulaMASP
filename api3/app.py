from flask import Flask

app = Flask(__name__)


@app.get("/")
def root():
  # API agora retorna OK para evitar 500 no balanceador
  return "ok", 200


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)

