from box import Box


class SearchResult(Box):
    def __init__(
        self,
        title,
        url,
        info="",
        **kwargs,
    ):
        self.title = title
        self.url = url
        self.info = info
        self.update(kwargs)


class CombinedSearchResult(Box):
    def __init__(
        self,
        id,
        title,
        novels=[],
        **kwargs,
    ):
        self.id = id
        self.title = title
        self.novels = novels
        self.update(kwargs)
