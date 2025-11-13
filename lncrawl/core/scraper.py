import base64
import logging
import os
import random
from io import BytesIO
from urllib.parse import urlparse

from PIL import Image
from requests import Session
from requests.exceptions import ProxyError
from requests.structures import CaseInsensitiveDict

from ..assets.user_agents import user_agents
from ..utils.ssl_no_verify import no_ssl_verification
from .exeptions import ScraperErrorGroup
from .proxy import get_a_proxy, remove_faulty_proxies
from .soup import SoupMaker
from .taskman import TaskManager

logger = logging.getLogger(__name__)


class Scraper(TaskManager, SoupMaker):
    # ------------------------------------------------------------------------- #
    # Constructor & Destructors
    # ------------------------------------------------------------------------- #
    def __init__(
        self,
        origin,
        workers=None,
        parser=None,
    ):
        """Creates a standalone Scraper instance.
        It is primarily being used as a superclass of the Crawler.

        Args:
        - origin (str): The origin URL of the scraper.
        - workers (int, optional): Number of concurrent workers to expect. Default: 10.
        - parser (Optional[str], optional): Desirable features of the parser. This can be the name of a specific parser
            ("lxml", "lxml-xml", "html.parser", or "html5lib") or it may be the type of markup to be used ("html", "html5", "xml").
        """
        self._soup_tool = SoupMaker(parser)
        self.make_soup = self._soup_tool.make_soup

        self.home_url = origin
        self.last_soup_url = ""
        self.use_proxy = os.getenv("use_proxy")

        self.init_scraper()
        self.change_user_agent()

        super(Scraper, self).__init__(workers)

    def __del__(self):
        if hasattr(self, "scraper"):
            self.scraper.close()
        super(Scraper, self).__del__()

    # ------------------------------------------------------------------------- #
    # Internal methods
    # ------------------------------------------------------------------------- #

    def __get_proxies(self, scheme, timeout=0):
        if self.use_proxy and scheme:
            return {scheme: get_a_proxy(scheme, timeout)}
        return {}

    def __process_request(self, method, url, **kwargs):
        method_call = getattr(self.scraper, method)
        assert callable(method_call), "No request method: {}".format(method)

        _parsed = urlparse(url)

        kwargs = kwargs or dict()
        retry = kwargs.pop("retry", 1)
        kwargs.setdefault("allow_redirects", True)
        kwargs["proxies"] = self.__get_proxies(_parsed.scheme)
        headers = kwargs.pop("headers", {})
        headers = CaseInsensitiveDict(headers)
        # headers.setdefault("Host", _parsed.hostname)
        headers.setdefault("Origin", self.home_url.strip("/"))
        headers.setdefault("Referer", self.last_soup_url or self.home_url)
        headers.setdefault("User-Agent", self.user_agent)
        kwargs["headers"] = {
            str(k).encode("ascii"): str(v).encode("ascii")
            for k, v in headers.items()
            if v
        }

        # Add Cloudflare cookie if it exists
        cf_cookie = os.getenv("cf_cookie")
        if cf_cookie:
            kwargs.setdefault("cookies", {})
            kwargs["cookies"]["cf_clearance"] = cf_cookie

        while retry >= 0:
            try:
                logger.debug(
                    "[{}] {}\n".format(method.upper(), url)
                    + ", ".join(["{}={}".format(k, v) for k, v in kwargs.items()])
                )

                with self.domain_gate(_parsed.hostname):
                    with no_ssl_verification():
                        response = method_call(url, **kwargs)
                        response.raise_for_status()
                        response.encoding = "utf8"

                self.cookies.update({x.name: x.value for x in response.cookies})
                return response
            except ScraperErrorGroup as e:
                if retry == 0:  # retry attempt depleted
                    raise e

                retry -= 1
                logger.debug("{}: {} | Retrying...".format(type(e).__qualname__, e), e)

                if isinstance(e, ProxyError):
                    for proxy_url in kwargs.get("proxies", {}).values():
                        remove_faulty_proxies(proxy_url)
                    kwargs["proxies"] = self.__get_proxies(_parsed.scheme, 5)

    # ------------------------------------------------------------------------- #
    # Helpers
    # ------------------------------------------------------------------------- #

    @property
    def origin(self):
        """Parsed self.home_url"""
        return urlparse(self.home_url)

    @property
    def headers(self):
        """Default request headers"""
        return dict(self.scraper.headers)

    def set_header(self, key, value):
        """Set default headers for next requests"""
        self.scraper.headers[key] = value

    @property
    def cookies(self):
        """Current session cookies"""
        return {x.name: x.value for x in self.scraper.cookies}

    def set_cookie(self, name, value):
        """Set a session cookie"""
        self.scraper.cookies.set(name, value)

    def absolute_url(self, url, page_url=None):
        url = str(url or "").strip().rstrip("/")
        if not url:
            return url
        if len(url) >= 1024 or url.startswith("data:"):
            return url
        if not page_url:
            page_url = str(self.last_soup_url or self.home_url)
        if url.startswith("//"):
            return self.home_url.split(":")[0] + ":" + url
        if url.find("//") >= 0:
            return url
        if url.startswith("/"):
            return self.home_url.strip("/") + url
        if page_url:
            return page_url.strip("/") + "/" + url
        return self.home_url + url

    def init_scraper(self, session=None):
        self.scraper = session or Session()

    def change_user_agent(self):
        self.user_agent = random.choice(user_agents)
        self.set_header("User-Agent", self.user_agent)

    # ------------------------------------------------------------------------- #
    # Downloaders
    # ------------------------------------------------------------------------- #

    def get_response(self, url, retry=1, timeout=(7, 301), **kwargs):
        """Fetch the content and return the response"""
        return self.__process_request(
            "get",
            url,
            retry=retry,
            timeout=timeout,
            **kwargs,
        )

    def post_response(self, url, data={}, retry=1, **kwargs):
        """Make a POST request and return the response"""
        return self.__process_request(
            "post",
            url,
            data=data,
            retry=retry,
            **kwargs,
        )

    def submit_form(
        self, url, data=None, multipart=False, headers={}, **kwargs
    ):
        """Simulate submit form request and return the response"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Content-Type",
            "multipart/form-data"
            if multipart
            else "application/x-www-form-urlencoded; charset=UTF-8",
        )
        return self.post_response(url, data=data, headers=headers, **kwargs)

    def download_file(self, url, output_file, **kwargs):
        """Download content of the url to a file"""
        response = self.__process_request("get", url, **kwargs)
        with open(output_file, "wb") as f:
            f.write(response.content)

    def download_image(self, url, headers={}, **kwargs):
        """Download image from url"""
        if url.startswith("data:"):
            content = base64.b64decode(url.split("base64,")[-1])
        else:
            headers = CaseInsensitiveDict(headers)
            headers.setdefault("Origin", None)
            headers.setdefault("Referer", None)
            # headers.setdefault(
            #     "Accept",
            #     "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.9",
            # )
            response = self.__process_request("get", url, headers=headers, **kwargs)
            content = response.content
        return Image.open(BytesIO(content))

    def get_json(self, url, headers={}, **kwargs):
        """Fetch the content and return the content as JSON object"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Accept",
            "application/json,text/plain,*/*",
        )
        response = self.get_response(url, headers=headers, **kwargs)
        return response.json()

    def post_json(self, url, data={}, headers={}):
        """Make a POST request and return the content as JSON object"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault("Content-Type", "application/json")
        headers.setdefault(
            "Accept",
            "application/json,text/plain,*/*",
        )
        response = self.post_response(url, data=data, headers=headers)
        return response.json()

    def submit_form_json(
        self, url, data={}, headers={}, multipart=False, **kwargs
    ):
        """Simulate submit form request and return the content as JSON object"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Accept",
            "application/json,text/plain,*/*",
        )
        response = self.submit_form(
            url, data=data, headers=headers, multipart=multipart, **kwargs
        )
        return response.json()

    def get_soup(self, url, headers={}, parser=None, **kwargs):
        """Fetch the content and return a BeautifulSoup instance of the page"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Accept",
            "text/html,application/xhtml+xml,application/xml;q=0.9",
        )
        response = self.get_response(url, **kwargs)
        self.last_soup_url = url
        return self.make_soup(response)

    def post_soup(
        self, url, data={}, headers={}, parser=None, **kwargs
    ):
        """Make a POST request and return BeautifulSoup instance of the response"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Accept",
            "text/html,application/xhtml+xml,application/xml;q=0.9",
        )
        response = self.post_response(url, data=data, headers=headers, **kwargs)
        return self.make_soup(response)

    def submit_form_for_soup(
        self, url, data={}, headers={}, multipart=False, parser=None, **kwargs
    ):
        """Simulate submit form request and return a BeautifulSoup instance of the response"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Accept",
            "text/html,application/xhtml+xml,application/xml;q=0.9",
        )
        response = self.submit_form(
            url, data=data, headers=headers, multipart=multipart, **kwargs
        )
        return self.make_soup(response)
