import requests
import logging
import time

DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_PATH = "./numista_py.log"

API_BASE_URL = "https://api.numista.com/api"
DEFAULT_API_VER = 2
DEFAULT_ENDPOINT_URI = "/coins"
DEFAULT_CURRENCY = "USD"  # 3-letter ISO 4217 currency code
DEFAULT_LANG = "en"  # ["en", "fr"]
DEFAULT_DATETIME_FMT = "%Y-%m-%d %H:%M:%S"

VALID_HTTP_METHODS = [
    "get",
    "post"
]

VALID_API_USER_SCOPES = [
    "view_collection",
    "edit_collection"
]


class Numista():
    """ Initialize the Class
    """
    def __init__(self,
                 debug: bool = False,
                 api_key: str = str(),
                 api_ver: int = DEFAULT_API_VER):
        self.inputs = dict()
        self.inputs['api_key'] = api_key
        self.inputs['api_ver'] = api_ver

        self.debug = debug
        self._call_api = getattr(self, f"_api_v{self.inputs['api_ver']}", None)

        # Store any oauth tokens generated
        # TODO: Create a dict template for this entry, and deep copy it when generating tokens
        # Update self._oauth_self() with template
        self.oauth_tokens = dict()

        # Add any alternate namings for methods and attributes
        self.get_catalogues = getattr(self, "get_catalogs", None)

        self._init_logger()

        if not self.inputs['api_key']:
            msg = "api_key is required to access the numista API"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        if not self._call_api:
            msg = f"An unrecognized API Version was provided, setting to version: {DEFAULT_API_VER}"
            self.logger.warning(msg)

        self.logger.info("Numista() has been initialized")

    def _init_logger(self, path: str = str()) -> None:
        """ Initialize logic for the logger
        """
        self.logger = logging
        debug = getattr(self, "debug", None)

        # TODO: Allow to easily modify log level
        if debug:
            level = logging.DEBUG
        else:
            level = DEFAULT_LOG_LEVEL

        # TODO: Add validation that path exists and is writable
        if not path:
            path = DEFAULT_LOG_PATH

        self.logger.basicConfig(filename=path,
                                filemode='a',
                                level=level,
                                datefmt='%Y-%m-%dT%H:%M:%S%z',
                                format='%(levelname)s:%(process)d:%(asctime)s:%(message)s')
        self.logger.info('Logger initialized')

    def _except_and_log(self, ex_type=ValueError, ex_msg: str = "", log: str = "") -> None:
        """ Raises an exception based on the type provided in ex_type, and logs to file
            If 'log' provided, this string will be added after the log header, before the exception
        """
        if not ex_msg:
            ex_msg = "An unspecified exception occured and no message was provided"

        try:
            raise ex_type(ex_msg)
        except Exception:
            self.logger.exception(log)

    def _api_client(self,
                    v_path: str = str(),
                    http_method: str = "get",
                    endpoint_uri: str = DEFAULT_ENDPOINT_URI,
                    body: object = dict(),
                    add_headers: dict = dict(),
                    **kwargs):
        """ Handles the raw send/recieve of data with the api
            kwargs are passed as params={} for requests
        """
        http_method = http_method.lower()

        if http_method not in VALID_HTTP_METHODS:
            msg = f"The provided HTTP Method ({http_method}) is not valid ({VALID_HTTP_METHODS})"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        if http_method == "post" and not body:
            msg = "The parameter 'body' (object) is required with http_method = 'post'."
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        api_url = API_BASE_URL + v_path + endpoint_uri  # https://api.numista.com/api/v2/coins

        self.logger.debug(f"Numista API Path: {api_url}")

        headers = {
            "Numista-API-Key": self.inputs['api_key'],  # TODO: Add log filters to auto obfuscate
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if add_headers:
            headers = {**headers, **add_headers}  # Merge

        # TODO: Add log filters to auto obfuscate
        log_headers = {k: v for k, v in headers.items()}
        log_headers['Numista-API-Key'] = f"***{log_headers['Numista-API-Key'][-4:]}"

        if log_headers.get("Authorization", None):
            log_headers['Authorization'] = f"Bearer ***{log_headers['Authorization'][-4:]}"

        self.logger.debug(f"Headers: {log_headers}")

        r = None

        self.logger.debug(f"HTTP Method: {http_method}")
        self.logger.debug("Attempting to send to API")
        if http_method == "get":
            r = requests.get(api_url, headers=headers, params=kwargs)

        elif http_method == "post":
            r = requests.post(api_url, headers=headers, params=kwargs, json=body)

        self.logger.debug("Completed API Attempt")

        # TODO: This should probably be handled a little better, such as evaluate the response
        #       code, and return more verbose error messages and logging.
        if r:
            self.logger.debug("API Request Succeeded")
            return self._result_format(data=r.json(), http_status=r.status_code, requests=r)
        else:
            self.logger.debug("API Request Failed")
            http_status = r.status_code if r.status_code else 404
            return self._result_format(data={}, http_status=http_status, failed=True, requests=r)

    def _api_v2(self, **kwargs):
        """ SHIM: Any logic that is API Version 2 specific
        """
        v = "/v2"
        self.logger.debug(f"API endpoint configured for: {v}")

        return self._api_client(v_path=v, **kwargs)

    def _result_format(self,
                       data: dict = dict(),
                       http_status: int = 0,
                       failed: bool = False,
                       **kwargs) -> dict:
        """ Format the result in a predictable and consistent way
        """
        result_format = {
            "data": data,
            "http_status": http_status,
            "failed": failed,
            "extra": kwargs
        }
        return result_format

    def _oauth_self(self, scopes: list = list(), **kwargs) -> dict:
        """ Authenticate yourself for OAuth
        """
        self.logger.debug("Attempting to authenticate ourself to the OAuth API")
        if not scopes:
            self.logger.info("Consider setting 'scopes' (list) in 'oauth_self' to atleast "
                             "include 'view_collection'")
            self.logger.debug("Overriding empty list and setting 'scopes' to ['view_collection']")
            scopes = ["view_collection"]

        for scope in scopes:
            if scope not in VALID_API_USER_SCOPES:
                msg = f"{scope} is not a valid user scope. Valid values: '{VALID_API_USER_SCOPES}'"
                self._except_and_log(ex_msg=msg)
                raise ValueError(msg)

        endpoint_uri = "/oauth_token"
        kwargs['grant_type'] = "client_credentials"  # Staticly set for this method
        # kwargs['code'] = None  # Only required for grant_type = "authorization_code"
        # kwargs['client_id'] = None  # Only required for grant_type = "authorization_code"
        # kwargs['client_secret'] = None  # Only required for grant_type = "authorization_code"
        # kwargs['redirect_uri'] = None  # Only required for grant_type = "authorization_code"
        kwargs['scope'] = ",".join(scopes)  # Parameter expects a str of comma-seperated values

        self.logger.debug(f"Calling API endpoint {endpoint_uri} to grant {kwargs['grant_type']} "
                          f"with scopes {kwargs['scope']}")

        result = self._call_api(http_method="get", endpoint_uri=endpoint_uri, **kwargs)
        status = result['http_status']

        self.logger.debug(f"OAuth request finished with status {status}")

        if status not in range(200, 299):
            msg = f"A Non HTTP 2xx status was returned ({status}) when attempting to authorize " \
                    "ourselves to OAuth. Please check logs for details."
            self.logger.critical(msg)
            self._except_and_log(ex_msg=result.json())
            raise ValueError(msg)

        # Trim 1 second to ensure we assume exp before actual exp and to account for process delay
        expires_in = result['data']['expires_in'] - 1
        expires_at = int(time.time() + expires_in)
        expries_date = self._datetime_from_epoch(epoch=expires_at)

        self.logger.debug(f"Token generated successfully and expires at {expries_date}")

        token = {
            "self": {
                "token": result['data']['access_token'],
                "user_id": result['data']['user_id'],
                "type": result['data']['token_type'],
                "exp_epoch": expires_at,
                "exp_date": expries_date
            }
        }
        self.oauth_tokens.update(token)

        return result

    def _datetime_from_epoch(self, epoch: int = 0, fmt: str = None) -> str:
        """ Convert an epoch time to datetime
        """
        if not fmt:
            fmt = DEFAULT_DATETIME_FMT

        try:
            d = time.strftime(fmt, time.localtime(epoch))
        except ValueError as err:
            self._except_and_log(ex_msg=err)

        return d

    def search_coins(self,
                     q: str = str(),
                     issuer: str = str(),
                     lang: str = DEFAULT_LANG,
                     **kwargs) -> dict:
        """ Search Numista for a Coin based on a search query and other parameters
        """
        endpoint_uri = "/coins"

        self.logger.debug(f"search_coins() | "
                          f"Attempting to search for coin at endpoint: {endpoint_uri}")
        self.logger.debug(f"Query: {q}")
        self.logger.debug(f"Issuer: {issuer}")
        self.logger.debug(f"Language: {lang}")
        self.logger.debug(f"KWARGS: {kwargs}")

        if not q:
            msg = "You must provide a query string to the parameter: 'q'. Ex: q='Kopecks'"
            print(msg)
            self._except_and_log(ex_msg=msg)
            q = 'Kopecks'
        else:
            kwargs['q'] = q

        kwargs['issuer'] = issuer
        kwargs['lang'] = lang

        return self._call_api(http_method="get", endpoint_uri=endpoint_uri, **kwargs)

    def get_issuers(self, lang: str = DEFAULT_LANG, **kwargs) -> dict:
        """ Retrieve the list of issuing countries and territories
        """
        endpoint_uri = "/issuers"

        self.logger.debug(f"get_issuers() | "
                          f"Attempting to retrieve issuers at endpoint: {endpoint_uri}")
        self.logger.debug(f"Language: {lang}")
        self.logger.debug(f"KWARGS: {kwargs}")

        return self._call_api(http_method="get", endpoint_uri=endpoint_uri, **kwargs)

    def get_catalogs(self, **kwargs) -> dict:
        """ Retrieve the list of catalogues used for coin references
            Redirected from self.get_catalogues()
        """
        endpoint_uri = "/catalogues"

        self.logger.debug(f"get_catalogs() | "
                          f"Attempting to retrieve catalogs at endpoint: {endpoint_uri}")
        self.logger.debug(f"KWARGS: {kwargs}")

        return self._call_api(http_method="get", endpoint_uri=endpoint_uri, **kwargs)

    def get_coin_by_id(self, coin_id: int = 0, lang: str = DEFAULT_LANG, **kwargs) -> dict:
        """ Find a coin by it's ID
        """
        endpoint_uri = f"/coins/{coin_id}"

        self.logger.debug(f"get_coin_by_id() | "
                          f"Attempting to fetch coin at endpoint: {endpoint_uri}")
        self.logger.debug(f"Coin ID: {coin_id}")
        self.logger.debug(f"Language: {lang}")
        self.logger.debug(f"KWARGS: {kwargs}")

        if not coin_id:
            msg = "coin_id (int) is a required field"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        kwargs['lang'] = lang

        return self._call_api(http_method="get", endpoint_uri=endpoint_uri, **kwargs)

    def get_coin_issues(self, coin_id: int = 0, lang: str = DEFAULT_LANG, **kwargs) -> dict:
        """ Get the issues of a coin
        """
        endpoint_uri = f"/coins/{coin_id}/issues"

        self.logger.debug(f"get_coin_issues() | "
                          f"Attempting to fetch issue at endpoint: {endpoint_uri}")
        self.logger.debug(f"Coin ID: {coin_id}")
        self.logger.debug(f"Language: {lang}")
        self.logger.debug(f"KWARGS: {kwargs}")

        if not coin_id:
            msg = "coin_id (int) is a required field"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        kwargs['lang'] = lang

        return self._call_api(http_method="get", endpoint_uri=endpoint_uri, **kwargs)

    def get_price_for_issue(self,
                            coin_id: int = 0,
                            issue_id: int = 0,
                            currency: str = DEFAULT_CURRENCY,
                            lang: str = DEFAULT_LANG,
                            **kwargs) -> dict:
        """ Get the issues of a coin
        """
        endpoint_uri = f"/coins/{coin_id}/issues/{issue_id}/prices"

        self.logger.debug(f"get_price_for_issue() | "
                          f"Attempting to fetch price for issue at endpoint: {endpoint_uri}")
        self.logger.debug(f"Coin ID: {coin_id}")
        self.logger.debug(f"Issue ID: {issue_id}")
        self.logger.debug(f"Currency: {currency}")
        self.logger.debug(f"Language: {lang}")
        self.logger.debug(f"KWARGS: {kwargs}")

        if not coin_id:
            msg = "coin_id (int) is a required field"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        if not issue_id:
            msg = "issue_id (int) is a required field"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        kwargs['lang'] = lang
        kwargs['currency'] = currency

        return self._call_api(http_method="get", endpoint_uri=endpoint_uri, **kwargs)

    def get_user_by_id(self, user_id: str = str(), lang: str = DEFAULT_LANG, **kwargs) -> dict:
        """ Get information about a user
        """
        endpoint_uri = f"/users/{user_id}"

        self.logger.debug(f"get_user_by_id() | "
                          f"Attempting to find user at endpoint: {endpoint_uri}")
        self.logger.debug(f"User ID: {user_id}")
        self.logger.debug(f"Language: {lang}")
        self.logger.debug(f"KWARGS: {kwargs}")

        if not user_id:
            msg = "user_id (int) is a required field"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        kwargs['lang'] = lang

        return self._call_api(http_method="get", endpoint_uri=endpoint_uri, **kwargs)

    def get_user_coins(self,
                       user_id: str = str(),
                       lang: str = DEFAULT_LANG,
                       coin: int = 0,
                       token_label: str = str(),
                       **kwargs) -> dict:
        """ Get the coins owned by a user
        """
        endpoint_uri = f"/users/{user_id}/collected_coins"

        self.logger.debug(f"get_user_coins() | "
                          f"Attempting to coin for user at endpoint: {endpoint_uri}")
        self.logger.debug(f"User ID: {user_id}")
        self.logger.debug(f"Language: {lang}")
        self.logger.debug(f"Coin ID (0=all): {coin}")
        self.logger.debug(f"Using Token with Label: {token_label}")
        self.logger.debug(f"KWARGS: {kwargs}")

        if not user_id:
            msg = "user_id (int) is a required field"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        if coin:
            kwargs['coin'] = coin
        else:
            msg = "No ID for 'coin' (int) provided, will return list of all coins"
            self.logger.info(msg)

        # TODO: This can be written SO much better
        token = None
        if token_label:
            msg = f"Attempting to load bearer token with label: {token_label}"
            self.logger.debug(msg)
            token = self.oauth_tokens.get(token_label, None)
            if token:
                self.logger.debug(f"Token loaded successfully for {token_label}")
            else:
                msg = f"No Token found for {token_label}"
                self.logger.error(msg)
                self._except_and_log(ex_msg=msg)
                raise ValueError(msg)

        else:
            msg = "A bearer token for the user auth was not supplied, " \
                  "attempting to load a token with label: 'self'"
            self.logger.info(msg)

            my_token = None
            gen_attempted = False
            while not my_token:
                my_token = self.oauth_tokens.get("self", None)
                if not my_token and not gen_attempted:
                    msg = "No token found under label 'self', attempting to generate it"
                    self.logger.debug(msg)

                    result = self._oauth_self(scopes=["view_collection"])
                    gen_attempted = True
                elif not my_token and gen_attempted:
                    msg = "Attempted to generate bearer token for 'self' and failed"
                    self.logger.critical(msg)
                    self._except_and_log(ex_msg=result.data)
                    raise ValueError(msg)
                    break  # Should be redundant, but just in case.
                # else: We got a token, so just continue
            token = my_token  # Last step after 'else: while loop'

        self.logger.debug(f"Token found: ***{token[-4:]}")

        if not token:
            msg = "Somehow we got this far without a token, but now it's time to stop. " \
                  "Probably time to file a bug, TIA. See logging for details"
            self.logger.critical(msg)
            ex_msg = "A critical error was found when trying to get coins with a token labeled " \
                     f"{token_label} in method 'get_user_coins()'"
            self._except_and_log(ex_msg=ex_msg)
            raise LookupError(ex_msg)

        kwargs['lang'] = lang

        add_headers = {
            "Authorization": f"Bearer {token['token']}"
        }

        return self._call_api(http_method="get", endpoint_uri=endpoint_uri,
                              add_headers=add_headers, **kwargs)
