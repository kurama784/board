from django.shortcuts import render, get_object_or_404, redirect

from boards.views.base import BaseBoardView
from boards.views.mixins import DispatcherMixin
from boards.models.post import Post
from boards.models.tag import Tag
from boards.forms import AddTagForm, PlainErrorList

class PostAdminView(BaseBoardView, DispatcherMixin):

    def get(self, request, post_id, form=None):
        user = self._get_user(request)
        if not user.is_moderator:
            redirect('index')

        post = get_object_or_404(Post, id=post_id)

        if not form:
            dispatch_result = self.dispatch_method(request, post)
            if dispatch_result:
                return dispatch_result
            form = AddTagForm()

        context = self.get_context_data(request=request)

        context['post'] = post

        context['tag_form'] = form

        return render(request, 'boards/post_admin.html', context)

    def post(self, request, post_id):
        user = self._get_user(request)
        if not user.is_moderator:
            redirect('index')

        post = get_object_or_404(Post, id=post_id)
        return self.dispatch_method(request, post)

    def delete_tag(self, request, post):
        tag_name = request.GET['tag']
        tag = get_object_or_404(Tag, name=tag_name)

        post.remove_tag(tag)

        return redirect('post_admin', post.id)

    def add_tag(self, request, post):
        form = AddTagForm(request.POST, error_class=PlainErrorList)
        if form.is_valid():
            tag_name = form.cleaned_data['tag']
            tag, created = Tag.objects.get_or_create(name=tag_name)

            post.add_tag(tag)
            return redirect('post_admin', post.id)
        else:
            return self.get(request, post.id, form)
