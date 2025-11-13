from box import Box


class Session(Box):
    def __init__(
        self,
        user_input="",
        output_path="",
        completed=False,
        pack_by_volume=False,
        download_chapters=[],
        good_file_name=None,
        no_append_after_filename=False,
        login_data=None,
        output_formats=dict(),
        headers=dict(),
        cookies=dict(),
        proxies=dict(),
        **kwargs,
    ):
        self.user_input = user_input
        self.output_path = output_path
        self.completed = completed
        self.pack_by_volume = pack_by_volume
        self.download_chapters = download_chapters
        self.good_file_name = good_file_name
        self.no_append_after_filename = no_append_after_filename
        self.login_data = login_data
        self.output_formats = output_formats
        self.headers = headers
        self.cookies = cookies
        self.proxies = proxies
        self.update(kwargs)
