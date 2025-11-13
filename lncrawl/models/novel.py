from enum import Enum
from box import Box

from ..assets.languages import language_codes


class NovelStatus(Enum):
    unknown = "Unknown"
    ongoing = "Ongoing"
    completed = "Completed"
    hiatus = "Hiatus"


class Novel(Box):
    def __init__(
        self,
        url,
        title,
        authors=[],
        cover_url=None,
        chapters=[],
        volumes=[],
        is_rtl=None,
        synopsis=None,
        language=None,
        novel_tags=[],
        has_manga=None,
        has_mtl=None,
        language_code=[],
        source=None,
        editors=[],
        translators=[],
        status=NovelStatus.unknown,
        genres=[],
        tags=[],
        description=None,
        original_publisher=None,
        english_publisher=None,
        novelupdates_url=None,
        **kwargs,
    ):
        self.url = url
        self.title = title
        self.authors = authors
        self.cover_url = cover_url
        self.chapters = chapters
        self.volumes = volumes
        self.is_rtl = is_rtl
        self.synopsis = synopsis
        self.language = language
        self.novel_tags = novel_tags
        self.has_manga = has_manga
        self.has_mtl = has_mtl
        self.language_code = language_code
        self.source = source
        self.editors = editors
        self.translators = translators
        self.status = status
        self.genres = genres
        self.tags = tags
        self.description = description
        self.original_publisher = original_publisher
        self.english_publisher = english_publisher
        self.novelupdates_url = novelupdates_url
        self.update(kwargs)

    @property
    def language(self):
        return language_codes.get(self.language_code, "Unknown")
