"""Summary

Attributes:
    API_BASE_URL (str): Base URL for the Numista API
    API_DOCS_URL (str): URL for the documentation of the Numista API
    API_SCHEMA_URL (str): URL for the schema of the Numista API
    DEFAULT_API_VER (int): Default version of the api to use
    DEFAULT_CURRENCY (str): Default 3-letter ISO 4217 currency code
    DEFAULT_DATETIME_FMT (str): Default format for DateTime strings
    DEFAULT_ENDPOINT_URI (str): Default endpoint URI
    DEFAULT_LANG (str): Default language for results
    DEFAULT_LOG_LEVEL (object): Default logging level for the logger
    DEFAULT_LOG_PATH (str): Default path for the log file
    DEFAULT_TOKEN_LABEL (str): Default label for new tokens
    HTTP_STATUS_RESPONSE_MESSAGE (dict): A dictionary of HTTP repsonse codes and messages
    VALID_API_USER_SCOPES (list): Valid user scopes supported by the API
    VALID_CATEGORY_TYPES (list): Valid categories supported by the API
    VALID_HTTP_METHODS (list): Valid HTTP methods supported by the API
    VALID_NUMISTA_GRADES (TYPE): Valid grading labels supported by the API
    VALID_OAUTH_GRANT_TYPES (TYPE): Valid permission grants supported by the API
"""
import requests
import logging
import time
import json
import ruamel.yaml
import validators

from iso4217 import Currency

API_BASE_URL = "https://api.numista.com/api"
API_DOCS_URL = "https://en.numista.com/api/doc/index.php"
API_SCHEMA_URL = "https://api.numista.com/api/doc/swagger.yaml"

DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_PATH = "/var/log/numista.log"
DEFAULT_API_VER = 3
DEFAULT_ENDPOINT_URI = "/types"
DEFAULT_CURRENCY = "USD"  # 3-letter ISO 4217 currency code
DEFAULT_LANG = "en"  # ["en", "fr", "es"]
DEFAULT_DATETIME_FMT = "%Y-%m-%d %H:%M:%S"
DEFAULT_TOKEN_LABEL = "unnamed_token"

HTTP_STATUS_RESPONSE_MESSAGE = {
    200: "Request successful",
    201: "The requested operation was accepted and successful",
    202: "The requested operation was accepted and successful",
    204: "The item has been deleted",
    400: "Invalid parameter or missing mandatory parameter",
    401: "Invalid or missing API key, or insufficient permission",
    404: "The requested item not found, or you are not allowed to access it",
    429: "Quota exceeded",
    501: "No user associated to your API key (for grant type 'client_credentials')"
}

VALID_HTTP_METHODS = [
    "get",
    "post",
    "patch",
    "delete"
]

# All values passed implicitely to _oauth() by _oauth_self()
VALID_API_USER_SCOPES = [
    "view_collection",
    "edit_collection"
]

VALID_CATEGORY_TYPES = [
    "",  # None = All
    "coin",
    "banknote",
    "exunomia"
]

VALID_OAUTH_GRANT_TYPES = [
    "authorization_code",
    "client_credentials"
]

VALID_NUMISTA_GRADES = [
    "g",
    "vg",
    "f",
    "vf",
    "xf",
    "au",
    "unc",
]


def load_yaml(yaml_path=None) -> dict:
    """Loads a YAML file by file path or URL

    Args:
        yaml_path (None, optional): The URL or file path of the source YAML doc

    Returns:
        dict: A dictionary of the parsed YAML doc

    Raises:
        ValueError: When yaml_path is empty
    """
    if not yaml_path:
        raise ValueError('a yaml file path was not provided, returning None')
    yml = ruamel.yaml.YAML(typ="safe")
    url = True if validators.url(yaml_path) else False
    if url:
        r = requests.get(API_SCHEMA_URL)
        parsed_yaml = yml.load(r.content)
    else:
        with open(yaml_path, "r") as f:
            parsed_yaml = yml.load(f)
    return {**parsed_yaml}


class Numista():
    """Initialize the Class

    Attributes:
        addCollectedItems (method): operationId inconsistency, backwards compatability fix
        getCatalogs (method): Alternate spelling of API perfered language
        inputs (dict): A dictionary of the original inputs when instantiated
        logger (object): The logger class is attached here
        myTokenGenerate (method): Helper to a private method
        oauthTokens (dict): Dictionary containing all generated tokens by label
    """
    def __init__(self,
                 debug: bool = False,
                 api_key: str = str(),
                 api_ver: int = DEFAULT_API_VER,
                 auto_self_token: bool = False,
                 log_path: str = DEFAULT_LOG_PATH):
        """Initialize the Class
        # noqa: E501

        Args:
            debug (bool, optional): Initialize the logger as level: DEBUG
            api_key (str, optional): Your Numista API key
            api_ver (int, optional): The API version to use (You probably dont want to change this)
            auto_self_token (bool, optional): Generate a self token on class instantiation
            log_path (str, optional): Desired path to log file (including filename)

        Raises:
            ValueError: When an API Key is not provided
        """
        self._debug = debug
        self._raw = dict()  # For shoving debug data into.
        self._init_logger(path=log_path)

        self.inputs = dict()
        self.inputs['api_key'] = api_key
        self.inputs['api_ver'] = api_ver

        self._call_api = getattr(self, f"_api_v{self.inputs['api_ver']}", None)

        # Store any oauth tokens generated
        self.oauthTokens = dict()

        # Add any alternate namings for methods and attributes
        self.getCatalogs = getattr(self, "getCatalogues", None)
        self.myTokenGenerate = getattr(self, "_oauth_self", None)

        if not self.inputs['api_key']:
            msg = "api_key is required to access the numista API"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        if not self._call_api:
            msg = f"An unrecognized API Version was provided, setting to version: {DEFAULT_API_VER}"
            self.logger.warning(msg)

        if auto_self_token:
            self.myTokenGenerate()

        # API inconsistency that will get patched someday probably. making break proof now.
        self.addCollectedItems = getattr(self, "addCollectedItem")

        self._schemas = dict()  # populated by getSchema()

        self.logger.info("Numista() has been initialized")

    #
    # Helpers
    #

    def _init_logger(self,
                     path: str = str()) -> None:
        """Initialize logic for the logger
        # noqa: E501

        Args:
            path (str, optional): Desired path to log file (including filename)
        """
        self.logger = logging
        debug = getattr(self, "_debug", None)

        # TODO: #9 | Allow to easily modify log level
        if debug:
            level = logging.DEBUG
        else:
            level = DEFAULT_LOG_LEVEL

        # TODO: #10 | Add validation that path exists and is writable
        if not path:
            path = DEFAULT_LOG_PATH

        self.logger.basicConfig(filename=path,
                                filemode='a',
                                level=level,
                                datefmt='%Y-%m-%dT%H:%M:%S%z',
                                format='%(levelname)s:%(process)d:%(asctime)s:%(message)s')
        self.logger.info('Logger initialized')

    def _except_and_log(self,
                        ex_type=ValueError,
                        ex_msg: str = "",
                        log: str = "") -> None:
        """Raises an exception based on the type provided in ex_type, and logs to file
        If 'log' provided, this string will be added after the log header, before the exception
        # noqa: E501

        Args:
            ex_type (exception, optional): The Exception type object (ValueError)
            ex_msg (str, optional): The message to use for the exception
            log (str, optional): An optional log message to preceed the ex_msg

        Raises:
            ex_type: Attempt to raise the exception to be logged, without actually raising
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
                    body: dict = dict(),
                    add_headers: dict = dict(),
                    **kwargs) -> dict:
        """Handles the raw send/recieve of data with the api
        kwargs are passed as params={} for requests
        # noqa: E501

        Args:
            v_path (str, optional): The 'version' part of the path. Example: "/v3"
            http_method (str, optional): The HTTP method to use for requests
            endpoint_uri (str, optional): the URI of the API Endpoint, comes after "/v3"
            body (dict, optional): The body or 'payload' of the request. Only used with POST/PATCH/PUT operations
            add_headers (dict, optional): Headers to add to the default headers. Format: dict({"header": "value"})
            **kwargs: Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI

        Returns:
            dict: Return a dictionary with the result data and other metadata

        Raises:
            ValueError: When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values
        """
        http_method = http_method.lower()

        self.logger.debug(f"Input kwargs: {kwargs}")

        if http_method not in VALID_HTTP_METHODS:
            msg = f"The provided HTTP Method ({http_method}) is not valid ({VALID_HTTP_METHODS})"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        if http_method == "post" and not body:
            msg = "The parameter 'body' (object) is required with http_method = 'post'."
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        api_url = API_BASE_URL + v_path + endpoint_uri  # https://api.numista.com/api/v3/items

        if body:
            self.logger.debug(f"body: {body}")

        headers = {
            "Numista-API-Key": self.inputs['api_key'],  # TODO: #11 | Add log filters to auto obfuscate  # noqa: E501
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if add_headers:
            headers = {**headers, **add_headers}  # Merge

        # TODO: #11 | Add log filters to auto obfuscate
        log_headers = {k: v for k, v in headers.items()}
        log_headers['Numista-API-Key'] = f"***{log_headers['Numista-API-Key'][-4:]}"

        if log_headers.get("Authorization", None):
            log_headers['Authorization'] = f"Bearer ***{log_headers['Authorization'][-4:]}"

        # Remove null values, let API enforce defaults instead of sending garbage params.
        new_kwargs = {k: v for (k, v) in kwargs.items() if v}
        kwargs = new_kwargs

        self.logger.debug(f"Numista API Path: {api_url}")
        self.logger.debug(f"URI Params: {kwargs}")
        self.logger.debug(f"Headers: {log_headers}")
        self.logger.debug(f"HTTP Method: {http_method}")
        self.logger.debug("Attempting to send to API")

        r = None
        if http_method == "get":
            r = requests.get(api_url, headers=headers, params=kwargs)
        elif http_method == "post":
            r = requests.post(api_url, headers=headers, params=kwargs, json=body)
        elif http_method == "patch":
            r = requests.patch(api_url, headers=headers, params=kwargs, json=body)
        elif http_method == "delete":
            r = requests.delete(api_url, headers=headers, params=kwargs)

        self.logger.debug("Completed API Attempt")

        if self._debug and r:
            self.logger.debug("Storing raw request in _raw['last_request']")
            self._raw['last_request'] = r

        # TODO: #12 | This all can be done better I think
        if r.status_code in range(100, 599):
            try:
                r.json()
            except Exception as err:
                if http_method != "delete":
                    # TODO: #12 | Find a better way to handle the response coming in from a delete.
                    msg = "An exception was found when trying 'r.json()' in _api_client()"
                    self.logger.info(msg)
                    self._except_and_log(ex_msg=err, log=msg)

                content = r.content
                self.logger.debug(f"Using raw data in content: {content}")

                try:
                    json.loads(content)
                except Exception as err:
                    msg = "An exception was found when trying json.loads(content) in _api_client()"
                    self.logger.info(msg)
                    self._except_and_log(ex_msg=err, log=msg)
                    data = {"content": r.content}  # Probably empty anyway
                else:
                    data = json.loads(content)
            else:
                data = r.json()

            self.logger.debug(f"API request succeeded, parsed data: {data}")

            result = self._result_format(data=data,
                                         http_status=r.status_code, requests=r)
        else:
            self.logger.debug("API request failed ungracefully")
            http_status = r.status_code if r.status_code else 0
            result = self._result_format(data=data, failed=True,
                                         http_status=http_status, requests=r)

        return result

    def _api_v3(self,
                **kwargs) -> dict:
        """SHIM: Any logic that is API Version 3 specific
        # noqa: E501

        Args:
            **kwargs: Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI

        Returns:
            dict: Return a dictionary with the result data and other metadata
        """
        v = "/v3"
        self.logger.debug(f"API endpoint configured for: {v}")

        return self._api_client(v_path=v, **kwargs)

    def _api_v2(self,
                **kwargs) -> dict:
        """SHIM: Any logic that is API Version 2 specific
        # noqa: E501

        Args:
            **kwargs: Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI

        Returns:
            dict: Return a dictionary with the result data and other metadata
        """
        v = "/v2"
        self.logger.debug(f"API endpoint configured for: {v}")

        return self._api_client(v_path=v, **kwargs)

    def _result_format(self,
                       data: dict = dict(),
                       http_status: int = 0,
                       failed: bool = False,
                       **kwargs) -> dict:
        """Format the result in a predictable and consistent way
        # noqa: E501

        Args:
            data (dict, optional): The data to be placed in the 'data' field
            http_status (int, optional): The HTTP Status Code of the response. Example: 201, 404, 529
            failed (bool, optional): Simple hint field to easily check if the request failed or was successful
            **kwargs: Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI

        Returns:
            dict: Return a dictionary with the result data and other metadata
        """
        result_format = {
            "data": data,
            "http_info": {
                "http_status": http_status,
                "http_msg": HTTP_STATUS_RESPONSE_MESSAGE[http_status]
            },
            "failed": failed,
            "extra": kwargs
        }
        return result_format

    def _oauth(self,
               grant_type: str = str(),
               code: str = str(),
               client_id: str = str(),
               client_secret: str = str(),
               redirect_uri: str = str(),
               scope: str = str(),
               state: str = str(),
               token_label: str = str(),
               **kwargs) -> dict:
        """Authenticate an API Key with OAuth
        # noqa: E501

        Args:
            grant_type (str, optional): Grant type "authorization_code" (default) or "client_credentials" Available values authorization_code, client_credentials
            code (str, optional): For grant type "authorization_code", this is the authorization code (mandatory for grant type "authorization_code")
            client_id (str, optional): For grant type "authorization_code", client ID (mandatory for grant type "authorization_code")
            client_secret (str, optional): For grant type "authorization_code", client secret, which is the same as the API key (mandatory for grant type "authorization_code")
            redirect_uri (str, optional): For grant type "authorization_code", repeat the redirect URI used to get the authorization code (mandatory for grant type "authorization_code")
            scope (str, optional): A comma-separated list (as a str) of permissions you are requesting (e.g. 'view_collection')
            state (str, optional): A value of your choice, which will be echoed in the redirection back to the redirect URI.
            token_label (str, optional): The Label of the token that is stored to use as authorization
            **kwargs: Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI

        Returns:
            dict: Return a dictionary with the result data and other metadata

        Raises:
            ValueError: When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values
        """
        endpoint_uri = "/oauth_token"

        if (not grant_type) or (grant_type not in VALID_OAUTH_GRANT_TYPES):
            msg = f"grant_type is a required parameter and must be one of {VALID_OAUTH_GRANT_TYPES}"
            self.logger.critical(msg)
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)
        else:
            self.logger.debug(f"grant_type set to {grant_type}")

        # Conditionally required fields
        if grant_type == "authorization_code":
            msg = None

            if code:
                kwargs['code'] = code
            else:
                msg = f"code is when grant_type='authorization_code'. Got: {code}"

            if client_id:
                kwargs['client_id'] = client_id
            else:
                msg = f"client_id is when grant_type='authorization_code'. Got: {client_id}"

            if client_secret:
                kwargs['client_secret'] = client_secret
            else:
                msg = f"client_secret is when grant_type='authorization_code'. Got: {client_secret}"

            if redirect_uri:
                kwargs['redirect_uri'] = redirect_uri
            else:
                msg = f"redirect_uri is when grant_type='authorization_code'. Got: {redirect_uri}"

            if msg:
                self.logger.critical(msg)
                self._except_and_log(ex_msg=msg)
                raise ValueError(msg)

        if not token_label:
            token_count = len(self.oauthTokens)
            token_label = f"{DEFAULT_TOKEN_LABEL}{token_count+1}"
            self.logger.warn(f"token_label is required but none provided. Setting to {token_label}")

        # Make sure scope is valid
        self.logger.debug(f"Validating scope string comma seperated list: {scope}")
        scopes = [s.strip() for s in scope.split(",") if s.strip() in VALID_API_USER_SCOPES]

        if not scopes:
            self.logger.info(f"No valid scopes found in scope: {scope} setting to view_collection")
        else:
            self.logger.debug(f"valid scopes found: {scopes}")

        kwargs['scope'] = ",".join(scopes) if scopes else "view_collection"
        kwargs['state'] = state
        kwargs['grant_type'] = grant_type

        result = self._call_api(http_method="get", endpoint_uri=endpoint_uri, **kwargs)

        status = result['http_info']['http_status']
        msg = result['http_info']['http_msg']

        self.logger.debug(f"OAuth request finished with HTTP status {status} & msg: {msg}")

        if status not in range(200, 299):
            msg = f"A Non HTTP 2xx status was returned ({status}) when attempting to authorize " \
                    "to OAuth. Please check logs for details. (Try Numista().debug=True)"
            self.logger.critical(msg)
            self._except_and_log(ex_msg=result.json())
            raise ValueError(msg)

        # Trim 1 second to ensure we assume exp before actual exp and to account for process delay
        expires_in = result['data']['expires_in'] - 1
        expires_at = int(time.time() + expires_in)
        expires_date = self._datetime_from_epoch(epoch=expires_at)

        self.logger.debug(f"Token generated successfully and expires at {expires_date}")

        # Format and store token
        token = {
            token_label: {
                "token": result['data']['access_token'],
                "user_id": result['data']['user_id'],
                "type": result['data']['token_type'],
                "scope": kwargs['scope'],
                "exp_epoch": expires_at,
                "exp_date": expires_date
            }
        }
        self.oauthTokens.update(token)
        self.logger.info(f"Token with label: {token_label} stored in dict(oauthTokens)")

        return self.oauthTokens[token_label]

    def _oauth_self(self,
                    scope: str = str(),
                    **kwargs) -> dict:
        """Authenticate yourself for OAuth
        # noqa: E501

        Args:
            scope (str, optional): A comma-separated list (as a str) of permissions you are requesting (e.g. 'view_collection')
            **kwargs: Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI

        Returns:
            dict: Return a dictionary with the result data and other metadata
        """
        self.logger.debug("Generating a token for our API Key")
        if not scope:
            scope = ", ".join(VALID_API_USER_SCOPES)
            self.logger.debug(f"No scope provided for _oauth_self(), using defaults : {scope}")

        g_type = "client_credentials"
        return self._oauth(grant_type=g_type, scope=scope, token_label="self", **kwargs)

    def _datetime_from_epoch(self,
                             epoch: int = int(),
                             fmt: str = None) -> str:
        """Convert an epoch time to datetime
        # noqa: E501

        Args:
            epoch (int, optional): The epoch int (seconds) to be converted to DATETIME string
            fmt (str, optional): The format for how the DATETIME string should be returned. Default: "%Y-%m-%d %H:%M:%S"

        Returns:
            str: Return the DATETIME string converted from epoch
        """
        if not fmt:
            fmt = DEFAULT_DATETIME_FMT

        try:
            d = time.strftime(fmt, time.localtime(epoch))
        except ValueError as err:
            self._except_and_log(ex_msg=err)

        return d

    def _get_token_by_label(self,
                            token_label: str = str(),
                            no_self: bool = False) -> str:
        """Retrieves a token by it's label
        If no label supplied, attempted to fetch 'self', oauth if doesn't exist
        # noqa: E501

        Args:
            token_label (str, optional): The Label of the token that is stored to use as authorization
            no_self (bool, optional): By default when you call this method with no label, a token is generated for 'self'. This bool controls that behavior

        Returns:
            str: Return the token for the label provided

        Raises:
            ValueError: When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values
        """
        # TODO: #13 | This can be written SO much better
        token = None
        if token_label:
            self.logger.debug(f"Attempting to fetch bearer token with label: {token_label}")
            token = self.oauthTokens.get(token_label, None)
            if token:
                self.logger.debug(f"Token fetched successfully for {token_label}")
            else:
                self.logger.info(f"No Token found for {token_label}")
        elif not token_label and no_self:
            self.logger.info("A Token label must be supplied, or allow a self token to be returned")
        else:
            msg = "A bearer token for the user auth was not supplied, " \
                  "attempting to load a token with label: 'self'"
            self.logger.info(msg)

            my_token = None
            gen_attempted = False
            while not my_token:
                my_token = self.oauthTokens.get("self", None)
                if not my_token and not gen_attempted:
                    msg = "No token found under label 'self', attempting to generate it"
                    self.logger.debug(msg)

                    # result = self._oauth_self(scopes=["view_collection"])
                    result = self.myTokenGenerate()
                    gen_attempted = True
                elif not my_token and gen_attempted:
                    msg = "Attempted to generate bearer token for 'self' and failed"
                    self.logger.critical(msg)
                    self._except_and_log(ex_msg=result.data)
                    raise ValueError(msg)
                    break  # Should be redundant, but just in case.
                # else: We got a token, so just continue
            token = my_token  # Last step after 'else: while loop'

        self.logger.debug("Token found")
        return token

    def _validate_body(self,
                       body: dict = dict()) -> bool:
        """Check if body is populated by something
        Enables consistent logging and reduction of code copypasta
        Can be expanded if parseable schema is added to this code in the future
        # noqa: E501

        Args:
            body (dict, optional): The body or 'payload' of the request. Only used with POST/PATCH/PUT operations

        Returns:
            bool: True: Body is valid, False: Body is not valid (Not fully implmented yet)
        """
        result = None
        if body:
            self.logger.debug(f"Validated body: {body}")
            result = True
        else:
            self.logger.info("Body is required for POST/PATCH operations")
            self.logger.info(f"Please see documentation at {API_DOCS_URL}")
            result = False

        return result

    def _validate_field_in(self,
                           field: str = str(),
                           in_iter: (list, set, tuple) = list()) -> str:
        """Accepts a field as a string, and checks if it is in the iterable (valid set)
        Returns the field if valid
        # noqa: E501

        Args:
            field (str, optional): The field to check
            in_iter (list, set, tuple, optional): The iterable that should be checked if field is in

        Returns:
            str: If the field is valid, you will receive
        """
        valid_iter_types = (list, set, tuple)
        result = str()

        self.logger.debug(f"Validating if {field} in {in_iter}")
        if isinstance(in_iter, valid_iter_types):
            result = str(field) if field in in_iter else str()
        else:
            msg = f"A non-iterable type ({type(in_iter)}) was provided to 'in_iter'. " \
                  f"Valid types: {valid_iter_types}"
            self.logger.warn(msg)

        return result

    def _fetch_api_schema(self) -> bool:
        """Fetch the schema defined in API_SCHEMA_URL
        """
        self._schemas = load_yaml(API_SCHEMA_URL)

    def validateGrade(self,
                      grade: str = str()) -> str:
        """Validates a grade.
        When grade is an empty string, returns a json string of valid grades
        # noqa: E501

        Args:
            grade (str, optional): The grade that should be validated. Example: "vg"

        Returns:
            str: Returns the input grade if valid
        """
        result = str()
        if grade:
            self.logger.debug(f"Validating Grade: {grade}")
            result = self._validate_field_in(field=grade, in_iter=VALID_NUMISTA_GRADES)
        else:
            self.logger.info("No value for grade provided, returning json string of valid grades")
            result = json.dumps(VALID_NUMISTA_GRADES)
            self.logger.debug(f"Valid Grades: {result}")

        return result

    def myToken(self) -> str:
        """Returns the token with label: 'self'
        Generates token if not present

        Returns:
            str: Returns your token ('self')
        """
        my_token = self.oauthTokens.get("self", None)
        if not my_token:
            self.logger.debug("My Token hasn't been generated yet, generating now...")
            my_token = self.myTokenGenerate()

        return my_token['token']

    def myTokenRefresh(self) -> str:
        """destroys and regenerates 'self' token

        Returns:
            str: Returns your new token ('self')
        """
        self.logger.debug("Destroying existing token 'self'")
        self.oauthTokens.pop('self')
        return self.myToken()

    def myUserId(self) -> str:
        """Returns the user_id from token with with label: 'self'

        Returns:
            str: Returns your user ID
        """
        my_token = self.oauthTokens.get("self", None)
        if not my_token:
            self.logger.debug("My Token hasn't been generated yet, generating now...")
            my_token = self.genMyToken()

        return my_token['user_id']

    def myTokenExp(self,
                   epoch: bool = False) -> str:
        """Returns the expiration from token with label: 'self'
        # noqa: E501

        Args:
            epoch (bool, optional): Controls whether epoch or DATETIME is returned. Default: Return DATETIME

        Returns:
            str: Returns the Expiration of your token. Always a string even when epoch: True
        """
        time_field = "exp_epoch" if epoch else "exp_date"
        my_token = self.oauthTokens.get("self", None)
        if not my_token:
            self.logger.debug("My Token hasn't been generated yet, generating now...")
            my_token = self.genMyToken()

        return my_token[time_field]

    def schemaFind(self,
                   operationId: str = str(),
                   http_method: str = "get",
                   flat: bool = True) -> dict:
        """Return a schema by operationId
        Fetches schema if first call
        # noqa: E501

        Args:
            operationId (str, optional): The ID of the operation as it's known by the API. This package's method names have been aligned to the API when applicable
            http_method (str, optional): The HTTP Method to fetch schema for. Usually one of: post, patch
            flat (bool, optional): Should the schema be returns with top level heirarchy intact, or flat. Flat is useful because the path and method keys are dynamic

        Returns:
            dict: Return a dictionary with the result data and other metadata

        Raises:
            ValueError: When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values
        """
        self.logger.debug("schemaFind()")
        self.logger.debug(f"Operation ID: {operationId}")
        self.logger.debug(f"HTTP Method: {http_method}")
        self.logger.debug(f"Flat Result?: {flat}")

        if not operationId:
            msg = "operationId (str) is a required field"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        if http_method not in VALID_HTTP_METHODS:
            msg = f"The provided http_method: {http_method} must be one of {VALID_HTTP_METHODS}"
            self.logger.info(msg)
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        if not getattr(self, "_schemas", None):
            self.logger.info(f"Fetching schema document from {API_SCHEMA_URL}")
            self._fetch_api_schema()

        result = {"paths": {}}

        # Looping over the Schema document
        # {"paths": {p: m}}
        # p = the path (key)
        # p_val = the dict of all the methods
        # m = the http_method (key)
        # m_val = the dict of all the http_method's k: v
        paths = self._schemas['paths']
        for p, p_val in paths.items():
            for m, m_val in p_val.items():
                if http_method == m and operationId == m_val['operationId']:
                    if flat:
                        result = {"http_method": m, "path": p, **m_val}
                    else:
                        result = {"paths": {p: {m: m_val}}}
        if not result:
            msg = f"The operationId: {operationId} for http_method: {http_method} was not found in schemas"  # noqa: E501
            self.logger.info(msg)

        self.logger.debug(f"Result: {result}")
        return result

    def schemaGenerateBody(self,
                           operationId: str = str(),
                           http_method: str = "post",
                           example: bool = True) -> dict:
        """Generate a body for an API http_method from the schema
        # noqa: E501

        Args:
            operationId (str, optional): The ID of the operation as it's known by the API. This package's method names have been aligned to the API when applicable
            http_method (str, optional): The HTTP Method to fetch schema for. Usually one of: post, patch
            example (bool, optional): Return a full but empty body from parsing schema, or just the example with dummy data. Note: Only example is currently valid

        Returns:
            dict: Return a dictionary with the result data and other metadata
        """
        self.logger.debug("schemaGenerateBody()")
        self.logger.debug(f"Operation ID: {operationId}")
        self.logger.debug(f"HTTP Method: {http_method}")

        if not example:
            example = True
            self.logger.info("Non-Example responses have been disabled for now, Overriding...")

        valid_methods = ["post", "patch"]
        if http_method not in valid_methods:
            msg = f"The HTTP method: {http_method} you provided isn't one of {valid_methods}. " \
                  "A body object is only needed for post or patch operations"
            self.logger.info(msg)

        if not operationId:
            msg = "An operationId was not provided, setting to 'addCollectedItems'"
            self.logger.debug(msg)
            operationId = "addCollectedItems"

        result = dict()

        schema = self.schemaFind(operationId=operationId, http_method=http_method, flat=True)

        if not schema:
            msg = f"No schema found for operationId: {operationId} with http_method: {http_method}"
            self.logger.debug(msg)
        else:
            if example:
                result = {**schema['requestBody']['content']['application/json']['example']}
            else:
                pass
                # Could actually parse schema... maybe later.
        return result

    #
    # API Methods (Ordered by Documentation)
    #

    def searchTypes(self,
                    q: str = str(),
                    issuer: str = str(),
                    category: str = str(),
                    page: int = 1,
                    count: int = 50,
                    lang: str = DEFAULT_LANG,
                    **kwargs) -> dict:
        """Search the catalogue for coin, banknote and exonumia types
        # noqa: E501

        Args:
            q (str, optional): Search query. Example: "Buffalo" for coins with buffalo's on them or that match the key word somehow
            issuer (str, optional): Issuer code. If provided, only the coins from the given issuer are returned.
            category (str, optional): If this parameter is provided, only items of the given category are returned. Available values : coin, banknote, exonumia
            page (int, optional): Page of results. Default value : 1
            count (int, optional): Results per page. Default value : 50
            lang (str, optional): Language. Available values : en, es, fr. Default value : en
            **kwargs: Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI

        Returns:
            dict: Return a dictionary with the result data and other metadata
        """
        endpoint_uri = "/types"

        self.logger.debug(f"types() | at endpoint: {endpoint_uri}")
        self.logger.debug(f"Query: {q}")
        self.logger.debug(f"Issuer: {issuer}")
        self.logger.debug(f"Category: {category}")
        self.logger.debug(f"Page: {page}")
        self.logger.debug(f"Count: {count}")
        self.logger.debug(f"Language: {lang}")
        self.logger.debug(f"KWARGS: {kwargs}")

        if not q:
            msg = "You must provide a query string to the parameter: 'q'. Ex: q='Kopecks'"
            print(msg)
            self._except_and_log(ex_msg=msg)
            q = 'Kopecks'
        else:
            kwargs['q'] = q

        if category not in VALID_CATEGORY_TYPES:
            msg = f"The Category provided ({category}) is not in the list of valid options: " \
                  f"({VALID_CATEGORY_TYPES}). Attempting with category: coins"
            self.logger.warn(msg)
            self._except_and_log(ex_msg=msg)
            kwargs['category'] = "coins"
        else:
            kwargs['category'] = category

        kwargs['issuer'] = issuer
        kwargs['lang'] = lang
        kwargs['page'] = page
        kwargs['count'] = count

        return self._call_api(http_method="get", endpoint_uri=endpoint_uri, **kwargs)

    def addType(self,
                lang: str = DEFAULT_LANG,
                body: dict = dict(),
                **kwargs) -> dict:
        """This endpoint allows to add a coin to the catalogue.
        It requires a specific permission associated to your API key.
        After adding a coin, you are required to add at least one issue with
        `POST /types/{type_id}/issues` || `addIssue()`
        # noqa: E501

        Args:
            lang (str, optional): Language. Available values : en, es, fr. Default value : en
            body (dict, optional): The body or 'payload' of the request. Only used with POST/PATCH/PUT operations
            **kwargs: Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI

        Returns:
            dict: Return a dictionary with the result data and other metadata

        Raises:
            ValueError: When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values
        """
        endpoint_uri = "/types"

        self.logger.debug(f"addType() at endpoint: {endpoint_uri}")
        self.logger.debug(f"Language: {lang}")
        self.logger.debug(f"Body: {body}")
        self.logger.debug(f"KWARGS: {kwargs}")

        if not self._validate_body(body):
            msg = "Body validation failed"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)
        else:
            self.logger.info("The Numista API Requires you to also add at least 1 "
                             "issue to this type.")
            kwargs['body'] = body

        kwargs['lang'] = lang

        return self._call_api(http_method="post", endpoint_uri=endpoint_uri, **kwargs)

    def getType(self,
                type_id: int = int(),
                lang: str = DEFAULT_LANG,
                **kwargs) -> dict:
        """Find a type by ID
        # noqa: E501

        Args:
            type_id (int, optional): If this parameter is provided, only items of the given type are returned.
            lang (str, optional): Language. Available values : en, es, fr. Default value : en
            **kwargs: Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI

        Returns:
            dict: Return a dictionary with the result data and other metadata

        Raises:
            ValueError: When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values
        """
        endpoint_uri = f"/types/{type_id}"

        self.logger.debug(f"getType() | at endpoint: {endpoint_uri}")
        self.logger.debug(f"Type ID: {type_id}")
        self.logger.debug(f"Language: {lang}")
        self.logger.debug(f"KWARGS: {kwargs}")

        if not type_id:
            msg = "type_id (int) is a required field"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        kwargs['lang'] = lang

        return self._call_api(http_method="get", endpoint_uri=endpoint_uri, **kwargs)

    def getIssues(self,
                  type_id: int = int(),
                  lang: str = DEFAULT_LANG,
                  **kwargs) -> dict:
        """Find the issues of a type
        # noqa: E501

        Args:
            type_id (int, optional): If this parameter is provided, only items of the given type are returned.
            lang (str, optional): Language. Available values : en, es, fr. Default value : en
            **kwargs: Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI

        Returns:
            dict: Return a dictionary with the result data and other metadata

        Raises:
            ValueError: When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values
        """
        endpoint_uri = f"/types/{type_id}/issues"

        self.logger.debug(f"getIssues() | at endpoint: {endpoint_uri}")
        self.logger.debug(f"Type ID: {type_id}")
        self.logger.debug(f"Language: {lang}")
        self.logger.debug(f"KWARGS: {kwargs}")

        if not type_id:
            msg = "type_id (int) is a required field"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        kwargs['lang'] = lang

        return self._call_api(http_method="get", endpoint_uri=endpoint_uri, **kwargs)

    def addIssue(self,
                 type_id: int = int(),
                 lang: str = DEFAULT_LANG,
                 body: dict = dict(),
                 **kwargs) -> dict:
        """This endpoint allows to add coin issues to the catalogue.
        It requires a specific permission associated to your API key.
        # noqa: E501

        Args:
            type_id (int, optional): If this parameter is provided, only items of the given type are returned.
            lang (str, optional): Language. Available values : en, es, fr. Default value : en
            body (dict, optional): The body or 'payload' of the request. Only used with POST/PATCH/PUT operations
            **kwargs: Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI

        Returns:
            dict: Return a dictionary with the result data and other metadata

        Raises:
            ValueError: When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values
        """
        endpoint_uri = f"/types{type_id}/issues"

        self.logger.debug(f"addIssue() | at endpoint: {endpoint_uri}")
        self.logger.debug(f"Type ID: {type_id}")
        self.logger.debug(f"Language: {lang}")
        self.logger.debug(f"Body: {body}")
        self.logger.debug(f"KWARGS: {kwargs}")

        if not type_id:
            msg = "type_id (int) is a required field"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        if not self._validate_body(body):
            msg = "Body validation failed"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)
        else:
            kwargs['body'] = body

        kwargs['lang'] = lang

        return self._call_api(http_method="post", endpoint_uri=endpoint_uri, **kwargs)

    def getPrices(self,
                  type_id: int = int(),
                  issue_id: int = int(),
                  currency: str = DEFAULT_CURRENCY,
                  lang: str = DEFAULT_LANG,
                  **kwargs) -> dict:
        """Get estimates for the price of an issue of a coin
        # noqa: E501

        Args:
            type_id (int, optional): If this parameter is provided, only items of the given type are returned.
            issue_id (int, optional): ID of the issue
            currency (str, optional): 3-letter ISO 4217 currency code. Default value : EUR
            lang (str, optional): Language. Available values : en, es, fr. Default value : en
            **kwargs: Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI

        Returns:
            dict: Return a dictionary with the result data and other metadata

        Raises:
            ValueError: When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values
        """
        endpoint_uri = f"/types/{type_id}/issues/{issue_id}/prices"

        self.logger.debug(f"getPrices() | at endpoint: {endpoint_uri}")
        self.logger.debug(f"Type ID: {type_id}")
        self.logger.debug(f"Issue ID: {issue_id}")
        self.logger.debug(f"Currency: {currency}")
        self.logger.debug(f"Language: {lang}")
        self.logger.debug(f"KWARGS: {kwargs}")

        if not type_id:
            msg = "type_id (int) is a required field"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        if not issue_id:
            msg = "issue_id (int) is a required field"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        # Munge string and check validity
        currency = currency.upper()
        currency = currency if getattr(Currency, currency.lower(), None) else DEFAULT_CURRENCY

        kwargs['lang'] = lang
        kwargs['currency'] = currency

        return self._call_api(http_method="get", endpoint_uri=endpoint_uri, **kwargs)

    def getIssuers(self,
                   lang: str = DEFAULT_LANG,
                   **kwargs) -> dict:
        """Retrieve the list of issuing countries and territories
        # noqa: E501

        Args:
            lang (str, optional): Language. Available values : en, es, fr. Default value : en
            **kwargs: Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI

        Returns:
            dict: Return a dictionary with the result data and other metadata
        """
        endpoint_uri = "/issuers"

        self.logger.debug(f"getIssuers() | at endpoint: {endpoint_uri}")
        self.logger.debug(f"Language: {lang}")
        self.logger.debug(f"KWARGS: {kwargs}")

        return self._call_api(http_method="get", endpoint_uri=endpoint_uri, **kwargs)

    def getCatalogues(self,
                      **kwargs) -> dict:
        """Retrieve the list of catalogues used for coin references
        Redirected from self.get_catalogs()
        # noqa: E501

        Args:
            **kwargs: Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI

        Returns:
            dict: Return a dictionary with the result data and other metadata
        """
        endpoint_uri = "/catalogues"

        self.logger.debug(f"getCatalogues() | at endpoint: {endpoint_uri}")
        self.logger.debug(f"KWARGS: {kwargs}")

        return self._call_api(http_method="get", endpoint_uri=endpoint_uri, **kwargs)

    def getUser(self,
                user_id: int = int(),
                lang: str = DEFAULT_LANG,
                **kwargs) -> dict:
        """Get information about a user
        # noqa: E501

        Args:
            user_id (int, optional): ID of the User
            lang (str, optional): Language. Available values : en, es, fr. Default value : en
            **kwargs: Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI

        Returns:
            dict: Return a dictionary with the result data and other metadata

        No Longer Raises:
            ValueError: When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values
        """
        if not user_id:
            msg = "user_id (int) is a required field, defaulting to myUserId()"
            self.logger.info(msg)
            user_id = self.myUserId()

        endpoint_uri = f"/users/{user_id}"

        self.logger.debug(f"getUser() | at endpoint: {endpoint_uri}")
        self.logger.debug(f"User ID: {user_id}")
        self.logger.debug(f"Language: {lang}")
        self.logger.debug(f"KWARGS: {kwargs}")

        kwargs['lang'] = lang

        return self._call_api(http_method="get", endpoint_uri=endpoint_uri, **kwargs)

    #
    # Endpoints requiring OAuth
    #

    def getUserCollections(self,
                           user_id: int = int(),
                           category: str = str(),
                           token_label: str = "self",
                           **kwargs) -> dict:
        """Get the list of collections owned by a user
        # noqa: E501

        Args:
            user_id (int, optional): ID of the User
            category (str, optional): If this parameter is provided, only items of the given category are returned. Available values : coin, banknote, exonumia
            token_label (str, optional): The Label of the token that is stored to use as authorization
            **kwargs: Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI

        Returns:
            dict: Return a dictionary with the result data and other metadata

        Raises:
            LookupError: A lookup for other data failed. Example: trying to find a token by a label that doesnt exist
        """
        if not user_id:
            msg = "user_id (int) is a required field, defaulting to myUserId()"
            self.logger.info(msg)
            user_id = self.myUserId()

        endpoint_uri = f"/users/{user_id}/collections"

        self.logger.debug(f"getUserCollections() | at endpoint: {endpoint_uri}")
        self.logger.debug(f"User ID: {user_id}")
        self.logger.debug(f"Category: {category}")
        self.logger.debug(f"Trying Token with Label: {token_label}")
        self.logger.debug(f"KWARGS: {kwargs}")

        if category not in VALID_CATEGORY_TYPES:
            msg = f"The Category provided ({category}) is not in the list of valid options: " \
                  f"({VALID_CATEGORY_TYPES}). Attempting with category: coins"
            self.logger.warn(msg)
            self._except_and_log(ex_msg=msg)
            kwargs['category'] = "coins"
        else:
            kwargs['category'] = category

        token_dict = self._get_token_by_label(token_label=token_label)
        token = token_dict['token']

        if not token:
            msg = "No token found"
            self.logger.critical(msg)
            ex_msg = "A critical error was found when trying to get a collection with " \
                     f"a token labeled: {token_label} in method 'getUserCollections()'"
            self._except_and_log(ex_msg=ex_msg)
            raise LookupError(ex_msg)

        add_headers = {
            "Authorization": f"Bearer {token}"
        }

        return self._call_api(http_method="get", endpoint_uri=endpoint_uri,
                              add_headers=add_headers, **kwargs)

    def getCollectedItems(self,
                          user_id: int = int(),
                          category: str = str(),
                          type_id: int = int(),
                          collection: int = int(),
                          token_label: str = "self",
                          **kwargs) -> dict:
        """Get the items (coins, banknotes, pieces of exonumia) owned by a user
        # noqa: E501

        Args:
            user_id (int, optional): ID of the User
            category (str, optional): If this parameter is provided, only items of the given category are returned. Available values : coin, banknote, exonumia
            type_id (int, optional): If this parameter is provided, only items of the given type are returned.
            collection (int, optional): Collection ID. If this parameter is provided, only items in the given collection are returned.
            token_label (str, optional): The Label of the token that is stored to use as authorization
            **kwargs: Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI

        Returns:
            dict: Return a dictionary with the result data and other metadata

        Raises:
            LookupError: A lookup for other data failed. Example: trying to find a token by a label that doesnt exist

        No Longer Raises:
            ValueError: When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values
        """
        if not user_id:
            msg = "user_id (int) is a required field, defaulting to myUserId()"
            self.logger.info(msg)
            user_id = self.myUserId()

        endpoint_uri = f"/users/{user_id}/collected_items"

        self.logger.debug(f"getCollectedItems() | at endpoint: {endpoint_uri}")
        self.logger.debug(f"User ID: {user_id}")
        self.logger.debug(f"Category: {category}")
        self.logger.debug(f"Type ID: {type_id}")
        self.logger.debug(f"Collection ID: {collection}")
        self.logger.debug(f"Using Token with Label: {token_label}")
        self.logger.debug(f"KWARGS: {kwargs}")

        if category not in VALID_CATEGORY_TYPES:
            msg = f"The Category provided ({category}) is not in the list of valid options: " \
                  f"({VALID_CATEGORY_TYPES}). Attempting with category: coins"
            self.logger.warn(msg)
            self._except_and_log(ex_msg=msg)
            kwargs['category'] = "coins"
        else:
            kwargs['category'] = category

        token_dict = self._get_token_by_label(token_label=token_label)
        token = token_dict['token']

        if not token:
            msg = "No token found"
            self.logger.critical(msg)
            ex_msg = "A critical error was found when trying to get a collection with " \
                     f"a token labeled: {token_label} in method 'getUserItems()'"
            self._except_and_log(ex_msg=ex_msg)
            raise LookupError(ex_msg)

        kwargs['type'] = type_id  # BUG: #5
        kwargs['collection'] = collection

        add_headers = {
            "Authorization": f"Bearer {token}"
        }

        return self._call_api(http_method="get", endpoint_uri=endpoint_uri,
                              add_headers=add_headers, **kwargs)

    def addCollectedItem(self,
                         user_id: int = int(),
                         body: dict = dict(),
                         token_label: str = "self",
                         **kwargs) -> dict:
        """Add an item in the user collection
        # noqa: E501

        Args:
            user_id (int, optional): ID of the User
            body (dict, optional): The body or 'payload' of the request. Only used with POST/PATCH/PUT operations
            token_label (str, optional): The Label of the token that is stored to use as authorization
            **kwargs: Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI

        Returns:
            dict: Return a dictionary with the result data and other metadata

        Raises:
            LookupError: A lookup for other data failed. Example: trying to find a token by a label that doesnt exist
            ValueError: When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values
        """
        if not user_id:
            msg = "user_id (int) is a required field, defaulting to myUserId()"
            self.logger.info(msg)
            user_id = self.myUserId()

        endpoint_uri = f"/users/{user_id}/collected_items"

        self.logger.debug(f"addCollectedItems() | at endpoint: {endpoint_uri}")
        self.logger.debug(f"User ID: {user_id}")
        self.logger.debug(f"Body: {body}")
        self.logger.debug(f"Trying Token with Label: {token_label}")
        self.logger.debug(f"KWARGS: {kwargs}")

        if not self._validate_body(body):
            msg = "Body validation failed"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)
        else:
            kwargs['body'] = body

        token_dict = self._get_token_by_label(token_label=token_label)
        token = token_dict['token']

        if not token:
            msg = "No token found"
            self.logger.critical(msg)
            ex_msg = "A critical error was found when trying to get a collection with " \
                     f"a token labeled: {token_label} in method 'addCollectedItemss()'"
            self._except_and_log(ex_msg=ex_msg)
            raise LookupError(ex_msg)

        add_headers = {
            "Authorization": f"Bearer {token}"
        }

        return self._call_api(http_method="post", endpoint_uri=endpoint_uri,
                              add_headers=add_headers, **kwargs)

    def getCollectedItem(self,
                         user_id: int = int(),
                         item_id: int = int(),
                         token_label: str = "self",
                         **kwargs) -> dict:
        """Get an item in a user's collection
        # noqa: E501

        Args:
            user_id (int, optional): ID of the User
            item_id (int, optional): ID of the collected item
            token_label (str, optional): The Label of the token that is stored to use as authorization
            **kwargs: Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI

        Returns:
            dict: Return a dictionary with the result data and other metadata

        Raises:
            LookupError: A lookup for other data failed. Example: trying to find a token by a label that doesnt exist
            ValueError: When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values
        """
        if not user_id:
            msg = "user_id (int) is a required field, defaulting to myUserId()"
            self.logger.info(msg)
            user_id = self.myUserId()

        endpoint_uri = f"/users/{user_id}/collected_items/{item_id}"

        self.logger.debug(f"getCollectedItem() | at endpoint: {endpoint_uri}")
        self.logger.debug(f"User ID: {user_id}")
        self.logger.debug(f"Item ID: {item_id}")
        self.logger.debug(f"Trying Token with Label: {token_label}")
        self.logger.debug(f"KWARGS: {kwargs}")

        if not item_id:
            msg = "item_id (int) is a required field"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        token_dict = self._get_token_by_label(token_label=token_label)
        token = token_dict['token']

        if not token:
            msg = "No token found"
            self.logger.critical(msg)
            ex_msg = "A critical error was found when trying to get a collection with " \
                     f"a token labeled: {token_label} in method 'getCollectedItem()'"
            self._except_and_log(ex_msg=ex_msg)
            raise LookupError(ex_msg)

        add_headers = {
            "Authorization": f"Bearer {token}"
        }

        return self._call_api(http_method="get", endpoint_uri=endpoint_uri,
                              add_headers=add_headers, **kwargs)

    def editCollectedItem(self,
                          user_id: int = int(),
                          item_id: int = int(),
                          body: dict = dict(),
                          token_label: str = "self",
                          **kwargs) -> dict:
        """Edit an item in a user's collection
        # noqa: E501

        Args:
            user_id (int, optional): ID of the User
            item_id (int, optional): ID of the collected item
            body (dict, optional): The body or 'payload' of the request. Only used with POST/PATCH/PUT operations
            token_label (str, optional): The Label of the token that is stored to use as authorization
            **kwargs: Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI

        Returns:
            dict: Return a dictionary with the result data and other metadata

        Raises:
            LookupError: A lookup for other data failed. Example: trying to find a token by a label that doesnt exist
            ValueError: When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values
        """
        if not user_id:
            msg = "user_id (int) is a required field, defaulting to myUserId()"
            self.logger.info(msg)
            user_id = self.myUserId()

        endpoint_uri = f"/users/{user_id}/collected_items/{item_id}"

        self.logger.debug(f"editCollectedItem() | at endpoint: {endpoint_uri}")
        self.logger.debug(f"User ID: {user_id}")
        self.logger.debug(f"Item ID: {item_id}")
        self.logger.debug(f"Body: {body}")
        self.logger.debug(f"Trying Token with Label: {token_label}")
        self.logger.debug(f"KWARGS: {kwargs}")

        if not item_id:
            msg = "item_id (int) is a required field"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        if not self._validate_body(body):
            msg = "Body validation failed"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)
        else:
            kwargs['body'] = body

        token_dict = self._get_token_by_label(token_label=token_label)
        token = token_dict['token']

        if not token:
            msg = "No token found"
            self.logger.critical(msg)
            ex_msg = "A critical error was found when trying to get a collection with " \
                     f"a token labeled: {token_label} in method 'editCollectedItem()'"
            self._except_and_log(ex_msg=ex_msg)
            raise LookupError(ex_msg)

        add_headers = {
            "Authorization": f"Bearer {token}"
        }

        return self._call_api(http_method="patch", endpoint_uri=endpoint_uri,
                              add_headers=add_headers, **kwargs)

    def deleteCollectedItem(self,
                            user_id: int = int(),
                            item_id: int = int(),
                            token_label: str = "self",
                            **kwargs) -> dict:
        """Delete an item from a user's collection
        # noqa: E501

        Args:
            user_id (int, optional): ID of the User
            item_id (int, optional): ID of the collected item
            token_label (str, optional): The Label of the token that is stored to use as authorization
            **kwargs: Other fields that need to be passed. Typically, **kwargs: Other fields that need to be passed. Typically, KWARGS are passed as GET paramters in the URI

        Returns:
            dict: Return a dictionary with the result data and other metadata

        Raises:
            LookupError: A lookup for other data failed. Example: trying to find a token by a label that doesnt exist
            ValueError: When an invalid value is provided. Example: a value of "string" to an input wanting a dictionary, or an invalid value that has a limited set of valid values
        """
        if not user_id:
            msg = "user_id (int) is a required field, defaulting to myUserId()"
            self.logger.info(msg)
            user_id = self.myUserId()

        endpoint_uri = f"/users/{user_id}/collected_items/{item_id}"

        self.logger.debug(f"editCollectedItem() | at endpoint: {endpoint_uri}")
        self.logger.debug(f"User ID: {user_id}")
        self.logger.debug(f"Item ID: {item_id}")
        self.logger.debug(f"Trying Token with Label: {token_label}")
        self.logger.debug(f"KWARGS: {kwargs}")

        if not item_id:
            msg = "item_id (int) is a required field"
            self._except_and_log(ex_msg=msg)
            raise ValueError(msg)

        token_dict = self._get_token_by_label(token_label=token_label)
        token = token_dict['token']

        if not token:
            msg = "No token found"
            self.logger.critical(msg)
            ex_msg = "A critical error was found when trying to get a collection with " \
                     f"a token labeled: {token_label} in method 'deleteCollectedItem()'"
            self._except_and_log(ex_msg=ex_msg)
            raise LookupError(ex_msg)

        add_headers = {
            "Authorization": f"Bearer {token}"
        }

        return self._call_api(http_method="delete", endpoint_uri=endpoint_uri,
                              add_headers=add_headers, **kwargs)
