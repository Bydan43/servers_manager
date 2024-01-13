$(document).ready(function () {
    $('tr').hover(
        function () {
            $(this).css('background-color', '#ddd');
        },
        function () {
            $(this).css('background-color', '');
        }
    );
});
