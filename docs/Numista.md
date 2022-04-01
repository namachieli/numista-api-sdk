#


## Numista
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L117)
```python 
Numista(
   debug: bool = False, api_key: str = str(), api_ver: int = DEFAULT_API_VER,
   auto__token: bool = False, log_path: str = DEFAULT_LOG_PATH
)
```


---
Initialize the Class


**Attributes**

* **addCollectedItems** (method) : operationId inconsistency, backwards compatability fix
* **getCatalogs** (method) : Alternate spelling of API perfered language
* **inputs** (dict) : A dictionary of the original inputs when instantiated
* **logger** (object) : The logger class is attached here
* **myTokenGenerate** (method) : Helper to a private method
* **oauthTokens** (dict) : Dictionary containing all generated tokens by label



**Methods:**


### .validateGrade
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L703)
```python
.validateGrade(
   grade: str = str()
)
```

---
Validates a grade.
When grade is an empty string, returns a json string of valid grades


**Args**

* **grade** (str, optional) : The grade that should be validated. Example: "vg"


**Returns**

* **str**  : Returns the input grade if valid


### .myToken
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L726)
```python
.myToken()
```

---
Returns the token with label: 'self'
Generates token if not present


**Returns**

* **str**  : Returns your token ('self')


### .myTokenRefresh
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L740)
```python
.myTokenRefresh()
```

---
destroys and regenerates 'self' token


**Returns**

* **str**  : Returns your new token ('self')


### .myUserId
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L750)
```python
.myUserId()
```

---
Returns the user_id from token with with label: 'self'


**Returns**

* **str**  : Returns your user ID


### .myTokenExp
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L763)
```python
.myTokenExp(
   epoch: bool = False
)
```

---
Returns the expiration from token with label: 'self'


**Args**

* **epoch** (bool, optional) : Controls whether epoch or DATETIME is returned. Default: Return DATETIME


**Returns**

* **str**  : Returns the Expiration of your token. Always a string even when epoch: True


### .schemaFind
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L782)
```python
.schemaFind(
   operationId: str = str(), http_method: str = 'get', flat: bool = True
)
```

---
Return a schema by operationId
Fetches schema if first call


**Args**

* **operationId** (str, optional) : The ID of the operation as it's known by the API. This package's method names have been aligned to the API when applicable
* **http_method** (str, optional) : The HTTP Method to fetch schema for. Usually one of: post, patch
* **flat** (bool, optional) : Should the schema be returns with top level heirarchy intact, or flat. Flat is useful because the path and method keys are dynamic


**Returns**

* **dict**  : Return a dictionary with the result data and other metadata


**Raises**

* **ValueError**  : When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values


### .schemaGenerateBody
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L846)
```python
.schemaGenerateBody(
   operationId: str = str(), http_method: str = 'post', example: bool = True
)
```

---
Generate a body for an API http_method from the schema


**Args**

* **operationId** (str, optional) : The ID of the operation as it's known by the API. This package's method names have been aligned to the API when applicable
* **http_method** (str, optional) : The HTTP Method to fetch schema for. Usually one of: post, patch
* **example** (bool, optional) : Return a full but empty body from parsing schema, or just the example with dummy data. Note: Only example is currently valid


**Returns**

* **dict**  : Return a dictionary with the result data and other metadata


### .searchTypes
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L899)
```python
.searchTypes(
   q: str = str(), issuer: str = str(), category: str = str(), page: int = 1, count: int = 50,
   lang: str = DEFAULT_LANG, **kwargs
)
```

---
Search the catalogue for coin, banknote and exonumia types


**Args**

* **q** (str, optional) : Search query. Example: "Buffalo" for coins with buffalo's on them or that match the key word somehow
* **issuer** (str, optional) : Issuer code. If provided, only the coins from the given issuer are returned.
* **category** (str, optional) : If this parameter is provided, only items of the given category are returned. Available values : coin, banknote, exonumia
* **page** (int, optional) : Page of results. Default value : 1
* **count** (int, optional) : Results per page. Default value : 50
* **lang** (str, optional) : Language. Available values : en, es, fr. Default value : en
* **kwargs**  : Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI


**Returns**

* **dict**  : Return a dictionary with the result data and other metadata


### .addType
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L957)
```python
.addType(
   lang: str = DEFAULT_LANG, body: dict = dict(), **kwargs
)
```

---
This endpoint allows to add a coin to the catalogue.
It requires a specific permission associated to your API key.
After adding a coin, you are required to add at least one issue with
`POST /types/{type_id}/issues` || `addIssue()`


**Args**

* **lang** (str, optional) : Language. Available values : en, es, fr. Default value : en
* **body** (dict, optional) : The body or 'payload' of the request. Only used with POST/PATCH/PUT operations
* **kwargs**  : Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI


**Returns**

* **dict**  : Return a dictionary with the result data and other metadata


**Raises**

* **ValueError**  : When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values


### .getType
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L998)
```python
.getType(
   type_id: int = int(), lang: str = DEFAULT_LANG, **kwargs
)
```

---
Find a type by ID


**Args**

* **type_id** (int, optional) : If this parameter is provided, only items of the given type are returned.
* **lang** (str, optional) : Language. Available values : en, es, fr. Default value : en
* **kwargs**  : Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI


**Returns**

* **dict**  : Return a dictionary with the result data and other metadata


**Raises**

* **ValueError**  : When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values


### .getIssues
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L1032)
```python
.getIssues(
   type_id: int = int(), lang: str = DEFAULT_LANG, **kwargs
)
```

---
Find the issues of a type


**Args**

* **type_id** (int, optional) : If this parameter is provided, only items of the given type are returned.
* **lang** (str, optional) : Language. Available values : en, es, fr. Default value : en
* **kwargs**  : Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI


**Returns**

* **dict**  : Return a dictionary with the result data and other metadata


**Raises**

* **ValueError**  : When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values


### .addIssue
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L1066)
```python
.addIssue(
   type_id: int = int(), lang: str = DEFAULT_LANG, body: dict = dict(), **kwargs
)
```

---
This endpoint allows to add coin issues to the catalogue.
It requires a specific permission associated to your API key.


**Args**

* **type_id** (int, optional) : If this parameter is provided, only items of the given type are returned.
* **lang** (str, optional) : Language. Available values : en, es, fr. Default value : en
* **body** (dict, optional) : The body or 'payload' of the request. Only used with POST/PATCH/PUT operations
* **kwargs**  : Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI


**Returns**

* **dict**  : Return a dictionary with the result data and other metadata


**Raises**

* **ValueError**  : When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values


### .getPrices
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L1111)
```python
.getPrices(
   type_id: int = int(), issue_id: int = int(), currency: str = DEFAULT_CURRENCY,
   lang: str = DEFAULT_LANG, **kwargs
)
```

---
Get estimates for the price of an issue of a coin


**Args**

* **type_id** (int, optional) : If this parameter is provided, only items of the given type are returned.
* **issue_id** (int, optional) : ID of the issue
* **currency** (str, optional) : 3-letter ISO 4217 currency code. Default value : EUR
* **lang** (str, optional) : Language. Available values : en, es, fr. Default value : en
* **kwargs**  : Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI


**Returns**

* **dict**  : Return a dictionary with the result data and other metadata


**Raises**

* **ValueError**  : When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values


### .getIssuers
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L1161)
```python
.getIssuers(
   lang: str = DEFAULT_LANG, **kwargs
)
```

---
Retrieve the list of issuing countries and territories


**Args**

* **lang** (str, optional) : Language. Available values : en, es, fr. Default value : en
* **kwargs**  : Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI


**Returns**

* **dict**  : Return a dictionary with the result data and other metadata


### .getCatalogues
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L1182)
```python
.getCatalogues(
   **kwargs
)
```

---
Retrieve the list of catalogues used for coin references
Redirected from self.get_catalogs()


**Args**

* **kwargs**  : Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI


**Returns**

* **dict**  : Return a dictionary with the result data and other metadata


### .getUser
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L1201)
```python
.getUser(
   user_id: int = int(), lang: str = DEFAULT_LANG, **kwargs
)
```

---
Get information about a user


**Args**

* **user_id** (int, optional) : ID of the User
* **lang** (str, optional) : Language. Available values : en, es, fr. Default value : en
* **kwargs**  : Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI


**Returns**

* **dict**  : Return a dictionary with the result data and other metadata

---
No Longer Raises:
    ValueError: When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values

### .getUserCollections
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L1239)
```python
.getUserCollections(
   user_id: int = int(), category: str = str(), token_label: str = '', **kwargs
)
```

---
Get the list of collections owned by a user


**Args**

* **user_id** (int, optional) : ID of the User
* **category** (str, optional) : If this parameter is provided, only items of the given category are returned. Available values : coin, banknote, exonumia
* **token_label** (str, optional) : The Label of the token that is stored to use as authorization
* **kwargs**  : Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI


**Returns**

* **dict**  : Return a dictionary with the result data and other metadata


**Raises**

* **LookupError**  : A lookup for other data failed. Example: trying to find a token by a label that doesnt exist


### .getCollectedItems
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L1299)
```python
.getCollectedItems(
   user_id: int = int(), category: str = str(), type_id: int = int(),
   collection: int = int(), token_label: str = '', **kwargs
)
```

---
Get the items (coins, banknotes, pieces of exonumia) owned by a user


**Args**

* **user_id** (int, optional) : ID of the User
* **category** (str, optional) : If this parameter is provided, only items of the given category are returned. Available values : coin, banknote, exonumia
* **type_id** (int, optional) : If this parameter is provided, only items of the given type are returned.
* **collection** (int, optional) : Collection ID. If this parameter is provided, only items in the given collection are returned.
* **token_label** (str, optional) : The Label of the token that is stored to use as authorization
* **kwargs**  : Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI


**Returns**

* **dict**  : Return a dictionary with the result data and other metadata


**Raises**

* **LookupError**  : A lookup for other data failed. Example: trying to find a token by a label that doesnt exist

---
No Longer Raises:
    ValueError: When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values

### .addCollectedItem
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L1371)
```python
.addCollectedItem(
   user_id: int = int(), body: dict = dict(), token_label: str = '', **kwargs
)
```

---
Add an item in the user collection


**Args**

* **user_id** (int, optional) : ID of the User
* **body** (dict, optional) : The body or 'payload' of the request. Only used with POST/PATCH/PUT operations
* **token_label** (str, optional) : The Label of the token that is stored to use as authorization
* **kwargs**  : Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI


**Returns**

* **dict**  : Return a dictionary with the result data and other metadata


**Raises**

* **LookupError**  : A lookup for other data failed. Example: trying to find a token by a label that doesnt exist
* **ValueError**  : When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values


### .getCollectedItem
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L1430)
```python
.getCollectedItem(
   user_id: int = int(), item_id: int = int(), token_label: str = '', **kwargs
)
```

---
Get an item in a user's collection


**Args**

* **user_id** (int, optional) : ID of the User
* **item_id** (int, optional) : ID of the collected item
* **token_label** (str, optional) : The Label of the token that is stored to use as authorization
* **kwargs**  : Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI


**Returns**

* **dict**  : Return a dictionary with the result data and other metadata


**Raises**

* **LookupError**  : A lookup for other data failed. Example: trying to find a token by a label that doesnt exist
* **ValueError**  : When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values


### .editCollectedItem
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L1487)
```python
.editCollectedItem(
   user_id: int = int(), item_id: int = int(), body: dict = dict(), token_label: str = '',
   **kwargs
)
```

---
Edit an item in a user's collection


**Args**

* **user_id** (int, optional) : ID of the User
* **item_id** (int, optional) : ID of the collected item
* **body** (dict, optional) : The body or 'payload' of the request. Only used with POST/PATCH/PUT operations
* **token_label** (str, optional) : The Label of the token that is stored to use as authorization
* **kwargs**  : Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI


**Returns**

* **dict**  : Return a dictionary with the result data and other metadata


**Raises**

* **LookupError**  : A lookup for other data failed. Example: trying to find a token by a label that doesnt exist
* **ValueError**  : When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values


### .deleteCollectedItem
[source](https://github.com/namachieli/numista-api-sdk/blob/main/numista/numista.py/#L1554)
```python
.deleteCollectedItem(
   user_id: int = int(), item_id: int = int(), token_label: str = '', **kwargs
)
```

---
Delete an item from a user's collection


**Args**

* **user_id** (int, optional) : ID of the User
* **item_id** (int, optional) : ID of the collected item
* **token_label** (str, optional) : The Label of the token that is stored to use as authorization
* **kwargs**  : Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI


**Returns**

* **dict**  : Return a dictionary with the result data and other metadata


**Raises**

* **LookupError**  : A lookup for other data failed. Example: trying to find a token by a label that doesnt exist
* **ValueError**  : When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values

