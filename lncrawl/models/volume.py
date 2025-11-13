from box import Box


class Volume(Box):
    def __init__(
        self,
        id,
        title="",
        start_chapter=None,
        final_chapter=None,
        chapter_count=None,
        **kwargs,
    ):
        self.id = id
        self.title = title
        self.start_chapter = start_chapter
        self.final_chapter = final_chapter
        self.chapter_count = chapter_count
        self.update(kwargs)
