import os

base_media_path = os.path.abspath(os.path.join(os.path.realpath(__file__), '..', '..', '..', "media"))

documents_dir = os.path.join(base_media_path, "documents")
images_dir = os.path.join(base_media_path, "images")
video_dir = os.path.join(base_media_path, "video")
