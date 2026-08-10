import json

from src.database import init_db
from src.tools import (
    add_contact,
    delete_contact,
    get_bank_faqs,
    get_contacts,
    get_current_date_and_time,
    make_transfer_tool,
    read_client_information,
    read_transactions_information,
)

init_db()

config = {
    "configurable":{
        "user_id": 1
    }
}

def test_contacts():
    print("Testing the contact tools:")
    print("Adding Contacts:")
    result = add_contact.invoke({"tel": "687943253", "name": "Pepito"},config=config)
    print(f"{result}")
    print("Trying to add that same contact again:")
    error_result = add_contact.invoke({"tel": "687943253", "name": "Pepito"},config=config)
    print(error_result)
    print("Getting the contacts:")
    result = get_contacts.invoke({},config=config)
    print(f"{result}")
    print("Deleting the last added contact:")
    result = delete_contact.invoke({"tel": "687943253"}, config=config)
    print(result)

def test_transfers():
    print("Testing the transfers:")
    print("Making transfer:")
    result = make_transfer_tool.invoke({"amount": 25, "concepto": "Transacción prueba", "tel": "+34 600 556 101"}, config=config)
    print(result)
    print("Reading transactions:")
    result = json.dumps(read_transactions_information.invoke({}, config=config),indent = 2, ensure_ascii=False)
    print(result)

def test_client():
    print("Testing user info:")
    result = json.dumps(read_client_information.invoke({},config=config),indent = 2, ensure_ascii=False)
    print(result)

def test_time():
    print("Testing time telling tool:")
    result = get_current_date_and_time.invoke({})
    print(result)

def test_faqs():
    print("Testing the faqs:")
    result = get_bank_faqs.invoke({"query": "¿Cómo hago una trasnferencia?"})
    print(result)

if __name__ == "__main__":
    test_contacts()
    test_transfers()
    test_client()
    test_time()
    test_faqs()