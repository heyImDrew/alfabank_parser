# Stdlib:
import csv
import re
import time
from datetime import datetime
from time import mktime, strptime

def parse(stream):
    csvfile = (stream.file.read()).decode("1251")
    transactions = csvfile.split("\n")

    # Get account number
    account_number = re.search(r"Account number:.{0,34}", transactions[0])[0].split(":")[1]
    transactions.remove(transactions[1])

    # Find transactions where money were spent on items or services
    items_n_services_list = [
        transaction.split(";")[:-2]
        for transaction in transactions
        if transaction.find("Покупка товара / получение услуг") != -1
    ]
    for item in items_n_services_list:
        item[1] = re.split(r"Покупка товара \/ получение услуг    ", item[1])[1]
        item[2] = item[2][1:]
    items_n_services = [
        {
            "date": datetime.fromtimestamp(
                mktime(time.strptime(item[0].replace(".", " "), "%d %m %Y"))
            ),
            "account_from": account_number,
            "account_to": "Unknown",
            "category": "Unknown",
            "amount": item[2],
            "description": item[1],
            "keyword": item[1],
        }
        for item in items_n_services_list
    ]

    # Find cash replenishment transactions
    income_list = [
        transaction.split(";")
        for transaction in transactions
        if transaction.find("ПОПОЛНЕНИЕ КАРТСЧЕТОВ") != -1
    ]
    income = [
        {
            "date": datetime.fromtimestamp(
                mktime(time.strptime(transaction[0].replace(".", " "), "%d %m %Y"))
            ),
            "account_from": "Unknown",
            "account_to": account_number,
            "category": "Unknown",
            "amount": transaction[2],
            "description": "Cash replenishment",
            "keyword": "Replenishment",
        }
        for transaction in income_list
    ]

    # Find cash withdrawal transactions
    outcome_list = [
        transaction.split(";")
        for transaction in transactions
        if transaction.find("Получение денег") != -1
    ]
    outcome = [
        {
            "date": datetime.fromtimestamp(
                mktime(time.strptime(transaction[0].replace(".", " "), "%d %m %Y"))
            ),
            "account_from": account_number,
            "account_to": "Unknown",
            "category": "Unknown",
            "amount": transaction[2][1:],
            "description": "Cash withdrawal",
            "keyword": "Withdraw",
        }
        for transaction in outcome_list
    ]
    return items_n_services + income + outcome