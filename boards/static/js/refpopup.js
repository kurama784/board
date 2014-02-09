function $X(path, root) {
    return document.evaluate(path, root || document, null, 6, null);
}
function $x(path, root) {
    return document.evaluate(path, root || document, null, 8, null).singleNodeValue;
}

function $del(el) {
    if(el) el.parentNode.removeChild(el);
}

function $each(list, fn) {
    if(!list) return;
    var i = list.snapshotLength;
    if(i > 0) while(i--) fn(list.snapshotItem(i), i);
}

function addRefLinkPreview(node) {
    $each($X('.//a[starts-with(text(),">>")]', node || document), function(link) {
        link.addEventListener('mouseover', showPostPreview, false);
        link.addEventListener('mouseout', delPostPreview, false);
    });
}

function showPostPreview(e) {
    var doc = document;
    //ref id
    var pNum = $(this).text().match(/\d+/);

    if (pNum == null || pNum.length == 0) {
        return;
    }

    //position
    //var x = e.clientX + (doc.documentElement.scrollLeft || doc.body.scrollLeft) - doc.documentElement.clientLeft + 1;
    //var y = e.clientY + (doc.documentElement.scrollTop || doc.body.scrollTop) - doc.documentElement.clientTop;

    var x = e.clientX + (doc.documentElement.scrollLeft || doc.body.scrollLeft) + 2;
    var y = e.clientY + (doc.documentElement.scrollTop || doc.body.scrollTop);

    var cln = doc.createElement('div');
    cln.id = 'pstprev_' + pNum;
    cln.className = 'post_preview';

    cln.style.cssText = 'top:' + y + 'px;' + (x < doc.body.clientWidth/2 ? 'left:' + x + 'px' : 'right:' + parseInt(doc.body.clientWidth - x + 1) + 'px');

    cln.addEventListener('mouseout', delPostPreview, false);


    var mkPreview = function(cln, html) {
        cln.innerHTML = html;

        addRefLinkPreview(cln);
    };


    cln.innerHTML = "<div class=\"post\">" + gettext('Loading...') + "</div>";

    if($('div[id='+pNum+']').length > 0) {
        var postdata = $('div[id='+pNum+']').clone().wrap("<div/>").parent().html();

        mkPreview(cln, postdata);
    } else {
        $.ajax({
            url: '/api/post/' + pNum + '/?truncated'
        })
            .success(function(data) {
                var postdata = $(data).wrap("<div/>").parent().html();

                //make preview
                mkPreview(cln, postdata);

            })
            .error(function() {
                cln.innerHTML = "<div class=\"post\">"
                    + gettext('Post not found') + "</div>";
            });
    }

    $del(doc.getElementById(cln.id));

    //add preview
    $(cln).fadeIn(200);
    $('body').append(cln);
}

function delPostPreview(e) {
    var el = $x('ancestor-or-self::*[starts-with(@id,"pstprev")]', e.relatedTarget);
    if(!el) $each($X('.//div[starts-with(@id,"pstprev")]'), function(clone) {
        $del(clone)
    });
    else while(el.nextSibling) $del(el.nextSibling);
}

function addPreview() {
    $('.post').find('a').each(function() {
        showPostPreview($(this));
    });
}
