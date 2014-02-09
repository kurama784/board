from django.core.urlresolvers import reverse
import markdown
from markdown.inlinepatterns import Pattern
from markdown.util import etree
import boards

__author__ = 'neko259'


AUTOLINK_PATTERN = r'(https?://\S+)'
QUOTE_PATTERN = r'^(?<!>)(>[^>].+)$'
REFLINK_PATTERN = r'((>>)(\d+))'
SPOILER_PATTERN = r'%%([^(%%)]+)%%'
COMMENT_PATTERN = r'^(//(.+))'
STRIKETHROUGH_PATTERN = r'~(.+)~'


class TextFormatter():
    """
    An interface for formatter that can be used in the text format panel
    """

    name = ''

    # Left and right tags for the button preview
    preview_left = ''
    preview_right = ''

    # Left and right characters for the textarea input
    format_left = ''
    format_right = ''


class AutolinkPattern(Pattern):
    def handleMatch(self, m):
        link_element = etree.Element('a')
        href = m.group(2)
        link_element.set('href', href)
        link_element.text = href

        return link_element


class QuotePattern(Pattern, TextFormatter):
    name = ''
    preview_left = '<span class="quote">&gt; '
    preview_right = '</span>'

    format_left = '&gt;'

    def handleMatch(self, m):
        quote_element = etree.Element('span')
        quote_element.set('class', 'quote')
        quote_element.text = m.group(2)

        return quote_element


class ReflinkPattern(Pattern):
    def handleMatch(self, m):
        post_id = m.group(4)

        posts = boards.models.Post.objects.filter(id=post_id)
        if posts.count() > 0:
            ref_element = etree.Element('a')

            post = posts[0]

            ref_element.set('href', post.get_url())
            ref_element.text = m.group(2)

            return ref_element


class SpoilerPattern(Pattern, TextFormatter):
    name = 's'
    preview_left = '<span class="spoiler">'
    preview_right = '</span>'

    format_left = '%%'
    format_right = '%%'

    def handleMatch(self, m):
        quote_element = etree.Element('span')
        quote_element.set('class', 'spoiler')
        quote_element.text = m.group(2)

        return quote_element


class CommentPattern(Pattern, TextFormatter):
    name = ''
    preview_left = '<span class="comment">// '
    preview_right = '</span>'

    format_left = '//'

    def handleMatch(self, m):
        quote_element = etree.Element('span')
        quote_element.set('class', 'comment')
        quote_element.text = '//' + m.group(3)

        return quote_element


class StrikeThroughPattern(Pattern, TextFormatter):
    name = 's'
    preview_left = '<span class="strikethrough">'
    preview_right = '</span>'

    format_left = '~'
    format_right = '~'

    def handleMatch(self, m):
        quote_element = etree.Element('span')
        quote_element.set('class', 'strikethrough')
        quote_element.text = m.group(2)

        return quote_element


class ItalicPattern(TextFormatter):
    name = 'i'
    preview_left = '<i>'
    preview_right = '</i>'

    format_left = '_'
    format_right = '_'


class BoldPattern(TextFormatter):
    name = 'b'
    preview_left = '<b>'
    preview_right = '</b>'

    format_left = '__'
    format_right = '__'


class CodePattern(TextFormatter):
    name = 'code'
    preview_left = '<code>'
    preview_right = '</code>'

    format_left = '    '


class NeboardMarkdown(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        self._add_neboard_patterns(md)
        self._delete_patterns(md)

    def _delete_patterns(self, md):
        del md.parser.blockprocessors['quote']

        del md.inlinePatterns['image_link']
        del md.inlinePatterns['image_reference']

    def _add_neboard_patterns(self, md):
        autolink = AutolinkPattern(AUTOLINK_PATTERN, md)
        quote = QuotePattern(QUOTE_PATTERN, md)
        reflink = ReflinkPattern(REFLINK_PATTERN, md)
        spoiler = SpoilerPattern(SPOILER_PATTERN, md)
        comment = CommentPattern(COMMENT_PATTERN, md)
        strikethrough = StrikeThroughPattern(STRIKETHROUGH_PATTERN, md)

        md.inlinePatterns[u'autolink_ext'] = autolink
        md.inlinePatterns[u'spoiler'] = spoiler
        md.inlinePatterns[u'strikethrough'] = strikethrough
        md.inlinePatterns[u'comment'] = comment
        md.inlinePatterns[u'reflink'] = reflink
        md.inlinePatterns[u'quote'] = quote


def make_extension(configs=None):
    return NeboardMarkdown(configs=configs)

neboard_extension = make_extension()


def markdown_extended(markup):
    return markdown.markdown(markup, [neboard_extension], safe_mode=True)

formatters = [
    QuotePattern,
    SpoilerPattern,
    ItalicPattern,
    BoldPattern,
    CommentPattern,
    StrikeThroughPattern,
    CodePattern,
]
