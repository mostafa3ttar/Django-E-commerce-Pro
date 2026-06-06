// Alerts
$(document).ready(function () {
    setTimeout(function () {
        $(".custom-alert").fadeOut('slow', function () {
            $(this).remove();
        });
    }, 3000);
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

// Search 

const searchInput = document.querySelector('input[name="query"]');
const suggestionsBox = document.getElementById('search-suggestions');
let searchTimeout;

if (searchInput && suggestionsBox) {
    searchInput.addEventListener('input', function (e) {
        let queryValue = e.target.value.trim();

        if (queryValue.length < 2) {
            suggestionsBox.style.display = 'none';
            return;
        }

        clearTimeout(searchTimeout);

        searchTimeout = setTimeout(() => {
            fetch(`/list_product?query=${queryValue}`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.suggestions && data.suggestions.length > 0) {
                        let html = '<ul class="list-unstyled mb-0 py-2" style="margin:0; padding:0;">';

                        data.suggestions.forEach(item => {
                            html += `
                            <li class="suggestion-item px-3 py-2" style="cursor: pointer; transition: 0.2s; list-style: none;">
                                <a href="${item.url}" style="text-decoration: none; color: #0D1321; display: block;">
                                    <span class="fw-bold" style="font-family: 'Cormorant Garamond', serif; display:block;">${item.name}</span>
                                    <small class="text-muted" style="font-size: 11px;">In category: ${item.category}</small>
                                </a>
                            </li>
                        `;
                        });

                        html += '</ul>';
                        suggestionsBox.innerHTML = html;
                        suggestionsBox.style.display = 'block';
                    } else {
                        suggestionsBox.style.display = 'none';
                    }
                })
                .catch(err => console.error('Search AJAX Error:', err));
        }, 250);
    });

    document.addEventListener('click', function (e) {
        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.style.display = 'none';
        }
    });
}


// Cart
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.add-to-cart-btn').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();

            const form = this.closest('form');
            if (!form) return;

            const url = form.getAttribute('action');
            const formData = new FormData(form);

            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok');
                    return response.json();
                })
                .then(data => {
                    if (data.status === 'success') {
                        const badge = document.getElementById('cart-count-badge');
                        if (badge) {
                            badge.innerText = data.total_items;
                        }

                        const miniCart = document.getElementById('mini-cart-menu');
                        if (miniCart) {
                            miniCart.style.display = 'block';
                            setTimeout(() => { miniCart.style.display = ''; }, 2000);
                        }
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    });
});