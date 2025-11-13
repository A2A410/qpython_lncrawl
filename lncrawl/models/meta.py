from box import Box


class MetaInfo(Box):
    def __init__(
        self,
        novel=None,
        session=None,
        **kwargs,
    ):
        self.novel = novel
        self.session = session
        self.update(kwargs)
