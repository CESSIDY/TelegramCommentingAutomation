from dataclasses import dataclass


@dataclass
class CommentLoaderModel:
    message: str
    images: list
    videos: list

    def __init__(self, message: str, images: list, videos: list):
        self.message = message
        self.images = images
        self.videos = videos
