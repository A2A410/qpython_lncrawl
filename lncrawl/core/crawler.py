import hashlib
import logging
from abc import abstractmethod

from .cleaner import TextCleaner
from .scraper import Scraper

logger = logging.getLogger(__name__)


class Crawler(Scraper):
    """Blueprint for creating new crawlers"""

    has_manga = False
    has_mtl = False
    base_url = []
    language = ""

    # ------------------------------------------------------------------------- #
    # Constructor & Destructors
    # ------------------------------------------------------------------------- #
    def __init__(
        self,
        workers=None,
        parser=None,
    ):
        """
        Creates a standalone Crawler instance.

        Args:
        - workers (int, optional): Number of concurrent workers to expect. Default: 10.
        - parser (Optional[str], optional): Desirable features of the parser. This can be the name of a specific parser
            ("lxml", "lxml-xml", "html.parser", or "html5lib") or it may be the type of markup to be used ("html", "html5", "xml").
        """
        self.cleaner = TextCleaner()

        # Available in `search_novel` or `read_novel_info`
        self.novel_url = ""

        # Must resolve these fields inside `read_novel_info`
        self.novel_title = ""
        self.novel_author = ""
        self.novel_cover = None
        self.is_rtl = False
        self.novel_synopsis = ""
        self.novel_tags = []

        # Each item must contain these keys:
        # `id` - 1 based index of the volume
        # `title` - the volume title (can be ignored)
        self.volumes = []

        # Each item must contain these keys:
        # `id` - 1 based index of the chapter
        # `title` - the title name
        # `volume` - the volume id of this chapter
        # `volume_title` - the volume title (can be ignored)
        # `url` - the link where to download the chapter
        self.chapters = []

        # Initialize superclass
        super(Crawler, self).__init__(
            origin=self.base_url[0],
            workers=workers,
            parser=parser,
        )

    def __del__(self):
        # if hasattr(self, "volumes"):
        #     self.volumes.clear()
        # if hasattr(self, "chapters"):
        #     self.chapters.clear()
        super(Crawler, self).__del__()

    # ------------------------------------------------------------------------- #
    # Methods to implement in crawler
    # ------------------------------------------------------------------------- #

    def initialize(self):
        pass

    def login(self, email, password):
        pass

    def logout(self):
        pass

    def search_novel(self, query):
        """Gets a list of results matching the given query"""
        raise NotImplementedError()

    @abstractmethod
    def read_novel_info(self):
        """Get novel title, author, cover, volumes and chapters"""
        raise NotImplementedError()

    @abstractmethod
    def download_chapter_body(self, chapter):
        """Download body of a single chapter and return as clean html format."""
        raise NotImplementedError()

    # ------------------------------------------------------------------------- #
    # Utility methods that can be overriden
    # ------------------------------------------------------------------------- #

    def index_of_chapter(self, url):
        """Return the index of chapter by given url or 0"""
        url = self.absolute_url(url)
        for chapter in self.chapters:
            if chapter.url.rstrip("/") == url:
                return chapter.id
        return 0

    def extract_chapter_images(self, chapter):
        if not chapter.body:
            return

        chapter.setdefault("images", {})
        soup = self.make_soup(chapter.body)
        for img in soup.select("img[src]"):
            full_url = self.absolute_url(img["src"], page_url=chapter["url"])
            if not full_url.startswith("http"):
                continue

            filename = hashlib.md5(full_url.encode()).hexdigest() + ".jpg"
            img.attrs = {"src": "images/" + filename, "alt": filename}
            chapter.images[filename] = full_url

        chapter.body = soup.find("body").decode_contents()

    def download_chapters(
        self,
        chapters,
        fail_fast=False,
    ):
        futures = {
            index: self.executor.submit(self.download_chapter_body, chapter)
            for index, chapter in enumerate(chapters)
            if not chapter.success
        }
        yield len(chapters) - len(futures)

        self.resolve_futures(
            futures.values(),
            desc="Chapters",
            unit="item",
            fail_fast=fail_fast,
        )
        for (index, future) in futures.items():
            try:
                chapter = chapters[index]
                chapter.body = future.result()
                self.extract_chapter_images(chapter)
                chapter.success = True
            except Exception as e:
                chapter.body = ""
                chapter.success = False
                if isinstance(e, KeyboardInterrupt):
                    break
            finally:
                yield 1
