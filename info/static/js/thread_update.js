/*
 @licstart  The following is the entire license notice for the
 JavaScript code in this page.


 Copyright (C) 2013  neko259

 The JavaScript code in this page is free software: you can
 redistribute it and/or modify it under the terms of the GNU
 General Public License (GNU GPL) as published by the Free Software
 Foundation, either version 3 of the License, or (at your option)
 any later version.  The code is distributed WITHOUT ANY WARRANTY;
 without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the GNU GPL for more details.

 As additional permission under GNU GPL version 3 section 7, you
 may distribute non-source (e.g., minimized or compacted) forms of
 that code without the copy of the GNU GPL normally required by
 section 4, provided you include this license notice and a URL
 through which recipients can access the Corresponding Source.

 @licend  The above is the entire license notice
 for the JavaScript code in this page.
 */

var THREAD_UPDATE_DELAY = 10000;

var loading = false;
var lastUpdateTime = null;
var unreadPosts = 0

function blink(node) {
    var blinkCount = 2;

    var nodeToAnimate = node;
    for (var i = 0; i < blinkCount; i++) {
        nodeToAnimate = nodeToAnimate.fadeTo('fast', 0.5).fadeTo('fast', 1.0);
    }
}

function updateThread() {
    if (loading) {
        return;
    }

    loading = true;

    var threadPosts = $('div.thread').children('.post');

    var lastPost = threadPosts.last();
    var threadId = threadPosts.first().attr('id');

    var diffUrl = '/api/diff_thread/' + threadId + '/' + lastUpdateTime + '/';
    $.getJSON(diffUrl)
        .success(function(data) {
            var bottom = isPageBottom();

            var lastUpdate = '';

            var addedPosts = data.added;
            for (var i = 0; i < addedPosts.length; i++) {
                var postText = addedPosts[i];

                var post = $(postText);

                if (lastUpdate === '') {
                    lastUpdate = post.find('.pub_time').text();
                }

                post.appendTo(lastPost.parent());
                addRefLinkPreview(post[0]);

                lastPost = post;
                blink(post);
            }

            var updatedPosts = data.updated;
            for (var i = 0; i < updatedPosts.length; i++) {
                var postText = updatedPosts[i];

                var post = $(postText);

                if (lastUpdate === '') {
                    lastUpdate = post.find('.pub_time').text();
                }

                var postId = post.attr('id');

                var oldPost = $('div.thread').children('.post[id=' + postId + ']');
                
                oldPost.replaceWith(post);
                addRefLinkPreview(post[0]);

                blink(post);
            }

            // TODO Process deleted posts

            lastUpdateTime = data.last_update;
            loading = false;

            if (bottom) {
                var $target = $('html,body');
                $target.animate({scrollTop: $target.height()}, 1000);
            }

            var hasPostChanges = (updatedPosts.length > 0)
                || (addedPosts.length > 0);
            if (hasPostChanges) {
                updateMetadataPanel(lastUpdate);
            }

            updateBumplimitProgress(data.added.length);

            if (data.added.length + data.updated.length > 0) {
                showNewPostsTitle(data.added.length);
            }
        })
        .error(function(data) {
            // TODO Show error message that server is unavailable?

            loading = false;
        });
}

function isPageBottom() {
    var scroll = $(window).scrollTop() / ($(document).height()
        - $(window).height())

    return scroll == 1
}

function initAutoupdate() {
    loading = false;

    lastUpdateTime = $('.metapanel').attr('data-last-update');

    setInterval(updateThread, THREAD_UPDATE_DELAY);
}

function getReplyCount() {
    return $('.thread').children('.post').length
}

function getImageCount() {
    return $('.thread').find('img').length
}

function updateMetadataPanel(lastUpdate) {
    var replyCountField = $('#reply-count');
    var imageCountField = $('#image-count');

    replyCountField.text(getReplyCount());
    imageCountField.text(getImageCount());

    if (lastUpdate !== '') {
        var lastUpdateField = $('#last-update');
        lastUpdateField.text(lastUpdate);
        blink(lastUpdateField);
    }

    blink(replyCountField);
    blink(imageCountField);
}

/**
 * Update bumplimit progress bar
 */
function updateBumplimitProgress(postDelta) {
    var progressBar = $('#bumplimit_progress');
    if (progressBar) {
        var postsToLimitElement = $('#left_to_limit');

        var oldPostsToLimit = parseInt(postsToLimitElement.text());
        var postCount = getReplyCount();
        var bumplimit = postCount - postDelta + oldPostsToLimit;

        var newPostsToLimit = bumplimit - postCount;
        if (newPostsToLimit <= 0) {
            $('.bar-bg').remove();
            $('.thread').children('.post').addClass('dead_post');
        } else {
            postsToLimitElement.text(newPostsToLimit);
            progressBar.width((100 - postCount / bumplimit * 100.0) + '%');
        }
    }
}

var documentOriginalTitle = '';
/**
 * Show 'new posts' text in the title if the document is not visible to a user
 */
function showNewPostsTitle(newPostCount) {
    if (document.hidden) {
        if (documentOriginalTitle === '') {
            documentOriginalTitle = document.title;
        }
        unreadPosts = unreadPosts + newPostCount;
        document.title = '[' + unreadPosts + '] ' + documentOriginalTitle;

        document.addEventListener('visibilitychange', function() {
            if (documentOriginalTitle !== '') {
                document.title = documentOriginalTitle;
                documentOriginalTitle = '';
                unreadPosts = 0;
            }

            document.removeEventListener('visibilitychange', null);
        });
    }
}

/**
 * Clear all entered values in the form fields
 */
function resetForm(form) {
    form.find('input:text, input:password, input:file, select, textarea').val('');
    form.find('input:radio, input:checkbox')
             .removeAttr('checked').removeAttr('selected');
}


$(document).ready(function(){
    initAutoupdate();

    // Post form data over AJAX
    var threadId = $('div.thread').children('.post').first().attr('id');;

    var form = $('#form');
    var options = {
        success: updateOnPost,
        url: '/api/add_post/' + threadId + '/',
    };

    form.ajaxForm(options);

    function updateOnPost(response, statusText, xhr, $form) {
         var json = $.parseJSON(response);
         var status = json.status;

         form.children('.form-errors').remove();

         if (status === 'ok') {
             resetForm(form);
             updateThread();
         } else {
             var errors = json.errors;
             for (var i = 0; i < errors.length; i++) {
                 var fieldErrors = errors[i];

                 var error = fieldErrors.errors;

                 var errorList = $('<div class="form-errors">' + error
                     + '<div>');
                 errorList.appendTo(form);
             }
         }
     }
});
