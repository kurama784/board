import re
import string

from boards.models import Post
from boards.models.post import REGEX_REPLY

REFLINK_PREFIX = '>>'


class PostMixin:

    @staticmethod
    def _remove_invalid_links(text):
        """
        Replace invalid links in posts so that they won't be parsed.
        Invalid links are links to non-existent posts
        """

        for reply_number in re.finditer(REGEX_REPLY, text):
            post_id = reply_number.group(1)
            post = Post.objects.filter(id=post_id)
            if not post.exists():
                text = string.replace(text, REFLINK_PREFIX + post_id, post_id)

        return text
