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

function moveCaretToEnd(el) {
        if (typeof el.selectionStart == "number") {
            el.selectionStart = el.selectionEnd = el.value.length;
        } else if (typeof el.createTextRange != "undefined") {
            el.focus();
            var range = el.createTextRange();
            range.collapse(false);
            range.select();
        }
}

function addQuickReply(postId) {
    var textToAdd = '>>' + postId + '\n\n';
    var selection = window.getSelection().toString();
    if (selection.length > 0) {
        textToAdd += '> ' + selection + '\n\n';
    }

    var textAreaId = 'textarea';
    $(textAreaId).val($(textAreaId).val()+ textToAdd);

    var textarea = document.getElementsByTagName('textarea')[0];
    $(textAreaId).focus();
    moveCaretToEnd(textarea);

    $("html, body").animate({ scrollTop: $(textAreaId).offset().top }, "slow");
}
