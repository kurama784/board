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

function addImgPreview() {
    var margin = 20; //..change

    //keybind
    $(document).on('keyup.removepic', function(e) {
        if(e.which === 27) {
            $('.img-full').remove();
        }
    });

    $('body').on('click', '.thumb', function() {
        var el = $(this);
        var thumb_id = 'full' + el.find('img').attr('alt');

        if(!$('#'+thumb_id).length) {
            var img_w = el.find('img').attr('data-width');
            var img_h = el.find('img').attr('data-height');

            var win_w = $(window).width();
            var win_h = $(window).height();
            //new image size
            if (img_w > win_w) {
                img_h = img_h * (win_w/img_w) - margin;
                img_w = win_w - margin;
            }
            if (img_h > win_h) {
                img_w = img_w * (win_h/img_h) - margin;
                img_h = win_h - margin;
            }

            var img_pv = new Image();
            $(img_pv)
                .addClass('img-full')
                .attr('id', thumb_id)
                .attr('src', $(el).attr('href'))
                .appendTo($(el))
                .css({
                    'width': img_w,
                    'height': img_h,
                    'left': (win_w - img_w) / 2,
                    'top': ((win_h - img_h) / 2)
                })
                //scaling preview
                .mousewheel(function(event, delta) {
                    var cx = event.originalEvent.clientX,
                        cy = event.originalEvent.clientY,
                        i_w = parseFloat($(img_pv).width()),
                        i_h = parseFloat($(img_pv).height()),
                        newIW = i_w * (delta > 0 ? 1.25 : 0.8),
                        newIH = i_h * (delta > 0 ? 1.25 : 0.8);

                    $(img_pv).width(newIW);
                    $(img_pv).height(newIH);
                    //set position
                    $(img_pv)
                        .css({
                            left: parseInt(cx - (newIW/i_w) * (cx - parseInt($(img_pv).position().left, 10)), 10),
                            top:  parseInt(cy - (newIH/i_h) * (cy - parseInt($(img_pv).position().top, 10)), 10)
                        });

                    return false;
                }
            ).draggable({
                    addClasses: false,
                    stack: '.img-full'
                })
        }
        else {
            $('#'+thumb_id).remove();
        }
        //prevent default
        return false;
    });
}