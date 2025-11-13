from box import Box


class Chapter(Box):
    def __init__(
        self,
        id,
        url="",
        title="",
        volume=None,
        volume_title=None,
        body=None,
        images=dict(),
        success=False,
        **kwargs,
    ):
        self.id = id
        self.url = url
        self.title = title
        self.volume = volume
        self.volume_title = volume_title
        self.body = body
        self.images = images
        self.success = success
        self.update(kwargs)

    @staticmethod
    def without_body(item):
        result = item.copy()
        result.body = None
        return result
