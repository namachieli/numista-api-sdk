# Quickstart
https://en.numista.com/api/doc/index.php

```python
from numista import Numista
api_key = 'your key'
n = Numista(api_key=api_key)
n.get_user_by_id(user_id=2)

{'data': {'username': 'Xavier', 'avatar': 'https://en.numista.com/forum/avatars/20002403351640d537b85a.png'}, 'http_status': 200, 'failed': False, 'extra': {'requests': <Response [200]>}}
```

# Current Methods (WIP)
```
n.debug                 n.get_coin_issues(      n.get_user_by_id(       n.logger
n.get_catalogs(         n.get_issuers(          n.get_user_coins(       n.oauth_tokens
n.get_coin_by_id(       n.get_price_for_issue(  n.inputs                n.search_coins(
```