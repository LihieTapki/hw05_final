from django.core.files.uploadedfile import SimpleUploadedFile

from posts.tests.consts import NEW_SMALL_GIF, SMALL_GIF

uploaded = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif',
)

new_uploaded = SimpleUploadedFile(
    name='new_small.gif',
    content=NEW_SMALL_GIF,
    content_type='image/gif',
)
