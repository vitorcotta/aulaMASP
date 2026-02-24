from flask import Flask

app = Flask(__name__)


@app.get("/")
def root():
  # API propositalmente quebrada para o exercício
  return "erro", 500


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)

