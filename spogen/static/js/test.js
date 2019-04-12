$(function() {
    $('button').click(function() {
        $('#lyrics').load("{{ url_for('..',filename='txt/demo_test.txt') }}")
    });
});