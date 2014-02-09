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

/**
 * Add the desired characters to the start and end of selection.
 * @param start Start (left) text
 * @param end End (right) text
 * @returns {boolean}
 */
function addMarkToMsg(start, end) {
    if (end.length == 0) {
        return addTextToEachLineOfSelection(start);
    }

    var textarea = document.getElementsByTagName('textarea')[0];
    if(!textarea) return;
    if( document.selection ) {
        textarea.focus();
        sel = document.selection.createRange();
        sel.text = start + sel.text + end;
    } else if(textarea.selectionStart || textarea.selectionStart == '0') {
        textarea.focus();
        var startPos = textarea.selectionStart;
        var endPos = textarea.selectionEnd;
        textarea.value = textarea.value.substring(0, startPos) + start + textarea.value.substring(startPos, endPos) + end + textarea.value.substring( endPos, textarea.value.length );
    } else {
        textarea.value += start + end;
    }
    return false;
}

/**
 * Add text to the beginning of each selected line. Partially selected lines
 * are included
 * @param textToAdd
 * @returns {*}
 */
function addTextToEachLineOfSelection(textToAdd) {
    var editor, end, newValue, start, value, _ref, _ref1;
    editor = document.getElementsByTagName('textarea')[0];
    _ref = [editor.selectionStart, editor.selectionEnd], start = _ref[0], end = _ref[1];
    if (start == null) {
        return;
    }
    if (start === end) {
        return;
    }
    console.log("Selection range: start=" + start + " end=" + end);
    value = editor.value;
    _ref1 = getLinesRange(start, end, value), start = _ref1[0], end = _ref1[1];
    newValue = replaceLines(start, end, value, textToAdd);
    return editor.value = newValue;
}

function replaceLines(start, end, value, textToAdd) {
    var line, replacedText, text;
    text = value.slice(start, end);
    replacedText = ((function() {
        var _i, _len, _ref, _results;
        _ref = text.split("\n");
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            line = _ref[_i];
            _results.push(textToAdd + line);
        }
        return _results;
    })()).join("\n");
    return replaceSubstring(start, end, value, replacedText);
}

function replaceSubstring(start, end, string, replacingString) {
    return string.slice(0, start) + replacingString + string.slice(end);
}

function getLinesRange(start, end, value) {
    var i, rangeEnd, rangeStart, _i, _j, _ref, _ref1;
    if (value[start] === "\n") {
        start = start - 1;
    }
    _ref = [start, end], rangeStart = _ref[0], rangeEnd = _ref[1];
    for (i = _i = start; start <= 0 ? _i <= 0 : _i >= 0; i = start <= 0 ? ++_i : --_i) {
        if (value[i] === "\n") {
            break;
        }
        rangeStart = i;
    }
    for (i = _j = end, _ref1 = value.length; end <= _ref1 ? _j < _ref1 : _j > _ref1; i = end <= _ref1 ? ++_j : --_j) {
        if (value[i] === "\n") {
            break;
        }
        rangeEnd = i;
    }
    return [rangeStart, rangeEnd];
}