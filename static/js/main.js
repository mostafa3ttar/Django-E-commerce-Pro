// Alerts
$(document).ready(function () {
    setTimeout(function () {
        $(".custom-alert").fadeOut('slow', function () {
            $(this).remove();
        });
    }, 3000);
});

// Delete
$(document).ready(function () {
    $('.delete-btn').on('click', function () {
        var recordId = $(this).data('slug');
        var recordName = $(this).data('name');

        $('#recordName').text(recordName);

        $('#deleteForm').attr('action', '/delete/' + recordId + '/');
    });
});