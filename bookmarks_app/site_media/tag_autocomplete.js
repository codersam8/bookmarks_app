$(document).ready(function () {
    $("#id_tags").autocomplete(
        {source: '/bookmarks/ajax/tag/autocomplete/'}
    );
});
