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


// AJAX
$(document).ready(function () {
    $(document).on('click', '.category-btn', function (e) {
        var isProductPage = window.location.pathname.includes('/list_product');

        if (!isProductPage) {
            return; // to run href in html
        }

        e.preventDefault();  //to run ajax

        var btn = $(this);
        var categoryValue = btn.data('category');

        if (btn.is('button')) {
            $('button.category-btn').removeClass('active');
            btn.addClass('active');
        }

        $.ajax({
            url: '/list_product',
            type: 'GET',
            data: {
                'category': categoryValue
            },
            dataType: 'json',
            success: function (response) {
                $('#products-grid').html(response.html);

                var newUrl = window.location.protocol + "//" + window.location.host + '/list_product?category=' + categoryValue;
                window.history.pushState({ path: newUrl }, '', newUrl);
            },
            error: function (xhr, errmsg, err) {
                console.error("AJAX Error:", errmsg, err);
            }
        });
    });
});