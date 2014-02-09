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
 * Created with IntelliJ IDEA.
 * User: vurdalak
 * Date: 21.09.13
 * Time: 15:21
 * To change this template use File | Settings | File Templates.
 */

function addPopups() {

    $('a').each(function() {
        if($(this).text().indexOf('>>') == 0) {
            var refNum = $(this).text().match(/\d+/);

            if (refNum != null) {
                var self = $(this);

                $(this).mouseenter(function() {
                    $.get('/get_post/' + refNum, function(data) {
                        var popup = $('<div/>').html(data)

                        popup.dialog({
                            modal: false,
                            minHeight: 0,
                        });

                        popup.position({
                            my: "left+20 top+20",
                            at: "right bottom",
                            of: self
                        })

                        self.mouseleave(function() {
                            if (popup != null) {
                                popup.remove();
                            }
                        });
                    })
                });
            }
        }
    });

}
