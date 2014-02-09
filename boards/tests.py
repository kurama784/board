# coding=utf-8
import time
import logging
from django.core.paginator import Paginator

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse, NoReverseMatch

from boards.models import Post, Tag, Thread
from boards import urls
from neboard import settings

PAGE_404 = 'boards/404.html'

TEST_TEXT = 'test text'

NEW_THREAD_PAGE = '/'
THREAD_PAGE_ONE = '/thread/1/'
THREAD_PAGE = '/thread/'
TAG_PAGE = '/tag/'
HTTP_CODE_REDIRECT = 302
HTTP_CODE_OK = 200
HTTP_CODE_NOT_FOUND = 404

logger = logging.getLogger(__name__)


class PostTests(TestCase):

    def _create_post(self):
        return Post.objects.create_post(title='title',
                                        text='text')

    def test_post_add(self):
        """Test adding post"""

        post = self._create_post()

        self.assertIsNotNone(post, 'No post was created')

    def test_delete_post(self):
        """Test post deletion"""

        post = self._create_post()
        post_id = post.id

        Post.objects.delete_post(post)

        self.assertFalse(Post.objects.filter(id=post_id).exists())

    def test_delete_thread(self):
        """Test thread deletion"""

        opening_post = self._create_post()
        thread = opening_post.get_thread()
        reply = Post.objects.create_post("", "", thread=thread)

        thread.delete_with_posts()

        self.assertFalse(Post.objects.filter(id=reply.id).exists())

    def test_post_to_thread(self):
        """Test adding post to a thread"""

        op = self._create_post()
        post = Post.objects.create_post("", "", thread=op.get_thread())

        self.assertIsNotNone(post, 'Reply to thread wasn\'t created')
        self.assertEqual(op.get_thread().last_edit_time, post.pub_time,
                         'Post\'s create time doesn\'t match thread last edit'
                         ' time')

    def test_delete_posts_by_ip(self):
        """Test deleting posts with the given ip"""

        post = self._create_post()
        post_id = post.id

        Post.objects.delete_posts_by_ip('0.0.0.0')

        self.assertFalse(Post.objects.filter(id=post_id).exists())

    def test_get_thread(self):
        """Test getting all posts of a thread"""

        opening_post = self._create_post()

        for i in range(0, 2):
            Post.objects.create_post('title', 'text',
                                     thread=opening_post.get_thread())

        thread = opening_post.get_thread()

        self.assertEqual(3, thread.replies.count())

    def test_create_post_with_tag(self):
        """Test adding tag to post"""

        tag = Tag.objects.create(name='test_tag')
        post = Post.objects.create_post(title='title', text='text', tags=[tag])

        thread = post.get_thread()
        self.assertIsNotNone(post, 'Post not created')
        self.assertTrue(tag in thread.tags.all(), 'Tag not added to thread')
        self.assertTrue(thread in tag.threads.all(), 'Thread not added to tag')

    def test_thread_max_count(self):
        """Test deletion of old posts when the max thread count is reached"""

        for i in range(settings.MAX_THREAD_COUNT + 1):
            self._create_post()

        self.assertEqual(settings.MAX_THREAD_COUNT,
                         len(Thread.objects.filter(archived=False)))

    def test_pages(self):
        """Test that the thread list is properly split into pages"""

        for i in range(settings.MAX_THREAD_COUNT):
            self._create_post()

        all_threads = Thread.objects.filter(archived=False)

        paginator = Paginator(Thread.objects.filter(archived=False),
                              settings.THREADS_PER_PAGE)
        posts_in_second_page = paginator.page(2).object_list
        first_post = posts_in_second_page[0]

        self.assertEqual(all_threads[settings.THREADS_PER_PAGE].id,
                         first_post.id)

    def test_linked_tag(self):
        """Test adding a linked tag"""

        linked_tag = Tag.objects.create(name=u'tag1')
        tag = Tag.objects.create(name=u'tag2', linked=linked_tag)

        post = Post.objects.create_post("", "", tags=[tag])

        self.assertTrue(linked_tag in post.get_thread().tags.all(),
                        'Linked tag was not added')


class PagesTest(TestCase):

    def test_404(self):
        """Test receiving error 404 when opening a non-existent page"""

        tag_name = u'test_tag'
        tag = Tag.objects.create(name=tag_name)
        client = Client()

        Post.objects.create_post('title', TEST_TEXT, tags=[tag])

        existing_post_id = Post.objects.all()[0].id
        response_existing = client.get(THREAD_PAGE + str(existing_post_id) +
                                       '/')
        self.assertEqual(HTTP_CODE_OK, response_existing.status_code,
                         u'Cannot open existing thread')

        response_not_existing = client.get(THREAD_PAGE + str(
            existing_post_id + 1) + '/')
        self.assertEqual(PAGE_404,
                         response_not_existing.templates[0].name,
                         u'Not existing thread is opened')

        response_existing = client.get(TAG_PAGE + tag_name + '/')
        self.assertEqual(HTTP_CODE_OK,
                         response_existing.status_code,
                         u'Cannot open existing tag')

        response_not_existing = client.get(TAG_PAGE + u'not_tag' + '/')
        self.assertEqual(PAGE_404,
                         response_not_existing.templates[0].name,
                         u'Not existing tag is opened')

        reply_id = Post.objects.create_post('', TEST_TEXT,
                                            thread=Post.objects.all()[0]
                                            .thread)
        response_not_existing = client.get(THREAD_PAGE + str(
            reply_id) + '/')
        self.assertEqual(PAGE_404,
                         response_not_existing.templates[0].name,
                         u'Reply is opened as a thread')


class FormTest(TestCase):
    def test_post_validation(self):
        # Disable captcha for the test
        captcha_enabled = settings.ENABLE_CAPTCHA
        settings.ENABLE_CAPTCHA = False

        client = Client()

        valid_tags = u'tag1 tag_2 тег_3'
        invalid_tags = u'$%_356 ---'

        response = client.post(NEW_THREAD_PAGE, {'title': 'test title',
                                                 'text': TEST_TEXT,
                                                 'tags': valid_tags})
        self.assertEqual(response.status_code, HTTP_CODE_REDIRECT,
                         msg='Posting new message failed: got code ' +
                             str(response.status_code))

        self.assertEqual(1, Post.objects.count(),
                         msg='No posts were created')

        client.post(NEW_THREAD_PAGE, {'text': TEST_TEXT,
                                      'tags': invalid_tags})
        self.assertEqual(1, Post.objects.count(), msg='The validation passed '
                                                      'where it should fail')

        # Change posting delay so we don't have to wait for 30 seconds or more
        old_posting_delay = settings.POSTING_DELAY
        # Wait fot the posting delay or we won't be able to post
        settings.POSTING_DELAY = 1
        time.sleep(settings.POSTING_DELAY + 1)
        response = client.post(THREAD_PAGE_ONE, {'text': TEST_TEXT,
                                                 'tags': valid_tags})
        self.assertEqual(HTTP_CODE_REDIRECT, response.status_code,
                         msg=u'Posting new message failed: got code ' +
                             str(response.status_code))
        # Restore posting delay
        settings.POSTING_DELAY = old_posting_delay

        self.assertEqual(2, Post.objects.count(),
                         msg=u'No posts were created')

        # Restore captcha setting
        settings.ENABLE_CAPTCHA = captcha_enabled


class ViewTest(TestCase):

    def test_all_views(self):
        '''
        Try opening all views defined in ulrs.py that don't need additional
        parameters
        '''

        client = Client()
        for url in urls.urlpatterns:
            try:
                view_name = url.name
                logger.debug('Testing view %s' % view_name)

                try:
                    response = client.get(reverse(view_name))

                    self.assertEqual(HTTP_CODE_OK, response.status_code,
                            '%s view not opened' % view_name)
                except NoReverseMatch:
                    # This view just needs additional arguments
                    pass
                except Exception, e:
                    self.fail('Got exception %s at %s view' % (e, view_name))
            except AttributeError:
                # This is normal, some views do not have names
                pass
