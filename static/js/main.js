// Alerts
$(document).ready(function () {
    setTimeout(function () {
        $(".custom-alert").fadeOut('slow', function () {
            $(this).remove();
        });
    }, 3000);
});

