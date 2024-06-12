from flask import Flask, request, jsonify
import requests
import xml.etree.ElementTree as ET


app = Flask(__name__)


def get_currency_rate():
    url = "http://www.cbr.ru/scripts/XML_daily.asp"
    response = requests.get(url)
    root = ET.fromstring(response.content)

    rates = {}
    for valute in root.findall("Valute"):
        code = valute.find("CharCode").text
        value = valute.find("Value").text
        name = valute.find("Name").text
        rates[code] = {"name": name, "value": value}

    return rates


@app.route("/current_exchange_rate", methods=["GET"])
def current_exchange_rate():
    rates = get_currency_rate()
    return jsonify({"rates": rates})


@app.route("/<currency_code>", methods=["GET"])
def specific_currency_rate(currency_code):
    rates = get_currency_rate()
    if currency_code.upper() in rates:
        return jsonify({currency_code.upper(): rates[currency_code.upper()]})
    else:
        return "Currency not found."


@app.route("/", methods=["GET", "POST"])
def work():
    if request.method == "POST":
        currency_code = request.form["currency_code"]

        url = f"http://localhost:5000/{currency_code}"  # Меняйте URL на нужный (USD или EUR)
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            # Извлечение значения 'value' для ключа 'USD'
            result = data[currency_code]["value"]
            # Вывод значения 'value'
            result = float(result.replace(",", "."))
            return f"Результат: {result} <a href=''>Back</a>"
        else:
            return (
                "Ошибка при получении данных. Код ошибки: "
                + str(response.status_code)
                + "<a href=''>Back</a>"
            )
    rates = get_currency_rate()
    available_currencies = "Доступные валюты: <br>"
    for k, v in rates.items():
        available_currencies += f"{k} {v['name']}<br>"
    return f"""
        <form method="POST">
            Валюта: <input type="text" name="currency_code"><br>
            <input type="submit" value="Узнать курс"><br>
            {available_currencies}
        </form>
    """


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
