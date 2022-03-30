Pull Requests welcome!

API Documentation: https://en.numista.com/api/doc/index.php

# Installation
## Setup Virtual Environment
A Virtual Environment (venv) is a local copy of a runtime environment that is managed in a 'sandbox' that is seperate from your global environment. For example, your global python install is Python 3.8, but you need to run something in Python 2.7. You can make a virtual environment for Python 2.7, and then execute code from within that venv.

[Read more about Virtual Environments](https://www.geeksforgeeks.org/python-virtual-environment/?ref=rp)

```bash
mkdir ~/inventory && cd ~/inventory
python3 -m venv env
source ~/inventory/env/bin/activate
```

To exit the venv:
```bash
deactivate
```
## pypi.org
This will be added to PYPI soon

## Direct with PIP and SSH
Requires proper SSH Key access to be setup for your client.
```bash
pip install git+ssh://git@github.com/namachieli/numista-api-sdk
pip show numista
```
## HTTPS Clone and Local install
If you do not have an ssh key setup for git, you can clone the repository and install from a local copy.
```bash
mkdir -p ~/git && cd ~/git
git clone https://github.com/namachieli/numista-api-sdk
pip install ~/git/numista-api-sdk
pip show numista
```
# Quickstart
## Import
```python
from numista import Numista
api_key = 'your key'
n = Numista(api_key=api_key)
```
## Query a user
```python
user = n.getUser(user_id=2)
```
### Result:
```python
user
{'data': {'username': 'Xavier', 'avatar': 'https://en.numista.com/forum/avatars/20002403351640d537b85a.png'}, 'http_info': {'http_status': 200, 'http_msg': 'Request successful'}, 'failed': False, 'extra': {'requests': <Response [200]>}}
```
# Examples
## Search for a type
```python
escudos = n.searchTypes(q="Escudo", issuer='mexico')
```
### Result
```python
{'data': {'count': 20, 'types': [{'id': 236498, 'title': 'Medal - Ron Solera Bacardi', 'category': 'exonumia', 'issuer': {'code': 'mexique', 'name': 'Mexico'}, 'obverse_thumbnail': 'https://en.numista.com/catalogue/photos/mexique/6062e2f91b56c0.75792711-180.jpg', 'reverse_thumbnail': 'https://en.numista.com/catalogue/photos/mexique/6062e2f9a76b82.65792937-180.jpg'}, {<truncated>}], 'http_info': {'http_status': 200, 'http_msg': 'Request successful'}, 'failed': False, 'extra': {'requests': <Response [200]>}}
```
## Get a list of Issuers
```python
issuers = n.getIssuers()
```
### Result
```python
issuers
{'data': {'count': 4239, 'issuers': [{'code': 'abkhazia', 'name': 'Abkhazia', 'wikidata_id': 'Q23334'}, {'code': 'afghanistan', 'name': 'Afghanistan', 'wikidata_id': 'Q889'}, {<truncated>}]}, 'http_info': {'http_status': 200, 'http_msg': 'Request successful'}, 'failed': False, 'extra': {'requests': <Response [200]>}}
```
## Get a list of Catalogs/Catalogues
```python
catalogs = n.getCatalogs()  # Alternatively for our UK/EU friends n.getCatalogues()
```
### Result
```python
catalogs
{'data': {'count': 1587, 'catalogues': [{'id': 206, 'code': 'A', 'title': 'A Checklist of Islamic Coins', 'author': 'Stephen Album', 'publisher': 'Self-published', 'isbn13': '9780615562445'}, {'id': 241, 'code': 'AB', 'title': 'Catálogo de la moneda medieval castellano-leonesa', 'author': 'Fernando Álvarez Burgos', 'publisher': 'Vico-Segarra Editores', 'isbn13': '9788485711185'}, {<truncated>}]}, 'http_info': {'http_status': 200, 'http_msg': 'Request successful'}, 'failed': False, 'extra': {'requests': <Response [200]>}}
```
## OAuth and list Collections
The generated token is placed under the label `self` in `n.oauthTokens`

```python
n.myTokenGenerate()
{'token': '1234abcd5678efgh', 'user_id': 2, 'type': 'bearer', 'scope': 'view_collection,edit_collection', 'exp_epoch': 1648797646, 'exp_date': '2022-04-01 00:20:46'}

result = n.getUserCollections()
```
### Result
```python
result
{'data': {'count': 5, 'collections': [{'id': 43709, 'name': 'Misc - Non-US'}, {'id': 43708, 'name': 'Misc - US'}, {'id': 43706, 'name': 'Type - France'}, {'id': 43705, 'name': 'Type - Mexico'}, {'id': 43707, 'name': 'Type - US'}]}, 'http_info': {'http_status': 200, 'http_msg': 'Request successful'}, 'failed': False, 'extra': {'requests': <Response [200]>}}
```

## Get example schema for adding an item
**note** method would be either `post` for an add, or `patch` for an edit.
```python
schema = n.schemaGenerateBody(operationId="addCollectedItems", method="post")
```
### Result
```python
schema
{'type': 11331, 'issue': 63444, 'quantity': 1, 'grade': 'vf', 'for_swap': False, 'private_comment': 'Test with the API', 'price': {'value': 76, 'currency': 'EUR'}}
```
## Add an item to a collection
### Update schema fields to add a US 1833 Capped Bust Half Dollar
```python
schema['type'] = 10637
schema['issue'] = 73608
schema['grade'] = "au"
del schema['private_comment']
schema['price'] = {"value": 250, "currency": "USD"}
schema['collection'] = 43708

schema
{'type': 10637, 'issue': 73608, 'quantity': 1, 'grade': 'au', 'for_swap': False, 'price': {'value': 250, 'currency': 'USD'}, 'collection': 43708}
```
### Add the coin
```python
result = n.addCollectedItem(body=schema)
```
### Result
```python
result
{'data': {'id': 48567296, 'quantity': 1, 'type': {'id': 10637, 'title': '50 Cents / ½ Dollar &quot;Capped Bust Half Dollar&quot;', 'category': 'coin', 'issuer': {'code': 'etats-unis', 'name': 'United States'}}, 'issue': {'id': 73608, 'is_dated': True, 'year': 1833, 'gregorian_year': 1833, 'mintage': 5206000}, 'for_swap': False, 'grade': 'au', 'price': {'value': 250, 'currency': 'USD'}, 'collection': 43708}, 'http_info': {'http_status': 201, 'http_msg': 'The requested operation was accepted and successful'}, 'failed': False, 'extra': {'requests': <Response [201]>}}
```
## Get collected items from a collection
```python
result = n.getCollectedItems(collection=43708)
```
### Result
```python
result
{'data': {'item_count': 1, 'item_for_swap_count': 1, 'item_type_count': 1, 'item_type_for_swap_count': 1, 'items': [{'id': 48567296, 'quantity': 1, 'type': {'id': 10637, 'title': '50 Cents / ½ Dollar &quot;Capped Bust Half Dollar&quot;', 'category': 'coin', 'issuer': {'code': 'etats-unis', 'name': 'United States'}}, 'issue': {'id': 73608, 'is_dated': True, 'year': 1833, 'gregorian_year': 1833, 'mintage': 5206000}, 'for_swap': False, 'grade': 'au', 'price': {'value': 250, 'currency': 'USD'}, 'collection': {'id': 43708, 'name': 'Misc - US'}}]}, 'http_info': {'http_status': 200, 'http_msg': 'Request successful'}, 'failed': False, 'extra': {'requests': <Response [200]>}}
```
## Edit collected item
**note** This is a 'patch' operation, so only pass fields you want to edit, with desired new values
```python
body = {"price": {"value": 300, "currency": "USD"}}
result = n.editCollectedItem(item_id=48567296, body=body)
```
### Result
```python
result
{'data': {'id': 48567296, 'quantity': 1, 'type': {'id': 10637, 'title': '50 Cents / ½ Dollar &quot;Capped Bust Half Dollar&quot;', 'category': 'coin', 'issuer': {'code': 'etats-unis', 'name': 'United States'}}, 'issue': {'id': 73608, 'is_dated': True, 'year': 1833, 'gregorian_year': 1833, 'mintage': 5206000}, 'for_swap': False, 'grade': 'au', 'price': {'value': 300, 'currency': 'USD'}, 'collection': {'id': 43708, 'name': 'Misc - US'}}, 'http_info': {'http_status': 200, 'http_msg': 'Request successful'}, 'failed': False, 'extra': {'requests': <Response [200]>}}
```
## Delete collected item
```python
result = n.deleteCollectedItem(item_id=48567296)
```
### Result
```python
result
{'data': {'content': b''}, 'http_info': {'http_status': 204, 'http_msg': 'The item has been deleted'}, 'failed': False, 'extra': {'requests': <Response [204]>}}
```
# Documentation
Please see the [/docs](/docs) folder for verbose documentation on other methods and capabilities.

# Contribution
Pull requests are always welcome!
