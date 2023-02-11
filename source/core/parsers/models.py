from attrs import define

__all__ = ("Chapter", "Data")


@define
class Chapter:
    name: str
    url: str


@define
class Data:
    name: str
    image_url: str
    url: str
    last_chapter: Chapter
