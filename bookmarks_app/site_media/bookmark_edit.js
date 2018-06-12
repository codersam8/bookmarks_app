function bookmark_save() {
    var item = $(this).parent();
    var csrftoken = $('[name=csrfmiddlewaretoken]').val();
    var data = {
        'csrfmiddlewaretoken': csrftoken,
        url: item.find("id_url").var(),
        title: item.find("id_title").var(),
        tags: item.find("id_tags").var()
    };
    $.post('/bookmarks/save/?ajax', data, function (result) {
        if(result != "failure") {
            item.before($("li", result).get(0));
            item.remove();
            $("ul.bookmarks .edit").click(bookmark_edit);
        } else {
            alert("Failed to validate bookmark before saving.");
        }
    });
    return false;
}


function bookmark_edit() {
    var item = $(this).parent();
    var url = item.find(".title").attr("href");
    item.load("/bookmarks/save/?ajax&url=" + escape(url), null, function() {
        $('#save-form').submit(bookmark_save);
    });
    return false;
}

$(document).ready(function () {
    $("ul.bookmarks .edit").click(bookmark_edit);
});
