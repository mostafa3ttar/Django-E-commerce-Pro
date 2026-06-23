// Alerts
$(document).ready(function () {
    setTimeout(function () {
        $(".custom-alert").fadeOut('slow', function () {
            $(this).remove();
        });
    }, 4000);
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
        var type = btn.data('type'); // "category" or "collection"
        var slug = btn.data('slug');

        if (btn.is('button')) {
            $('button.category-btn').removeClass('active');
            btn.addClass('active');
        }

        var requestData = {};
        requestData[type] = slug;

        $.ajax({
            url: '/list_product',
            type: 'GET',
            data: requestData,
            dataType: 'json',
            success: function (response) {
                $('#products-grid').html(response.html);

                var newUrl = window.location.origin + '/list_product/?' + type + '=' + slug;
                window.history.pushState({ path: newUrl }, '', newUrl);
            },
            error: function (xhr, errmsg, err) {
                console.error("AJAX Error:", errmsg, err);
            }
        });
    });
});


// Search 
document.addEventListener('DOMContentLoaded', function () {
    const searchTrigger = document.querySelector('.search');
    const searchForm = document.querySelector('.searchform');
    const searchInput = document.querySelector('input[name="query"]');
    const suggestionsBox = document.getElementById('search-suggestions');
    let searchTimeout;

    if (searchTrigger && searchForm) {

        searchTrigger.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            searchForm.classList.toggle('active');

            if (searchForm.classList.contains('active') && searchInput) {
                searchInput.focus();
            }
        });

        document.addEventListener('click', function (e) {
            if (!searchForm.contains(e.target) && !searchTrigger.contains(e.target)) {
                searchForm.classList.remove('active');
                if (suggestionsBox) suggestionsBox.style.display = 'none';
            }
        });
    }

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
                                let metaInfo = item.category ? `Category: ${item.category}` : '';
                                if (item.collection) {
                                    metaInfo += metaInfo ? ` | Collection: ${item.collection}` : `Collection: ${item.collection}`;
                                }

                                html += `
                                    <li class="suggestion-item">
                                        <a href="${item.url}" class="suggestion-link">
                                            <span class="suggestion-name fw-bold">${item.name}</span>
                                            <small class="suggestion-category">${metaInfo}</small>
                                        </a>
                                    </li>`;
                            });
                            html += '</ul>';
                            suggestionsBox.innerHTML = html;
                            suggestionsBox.style.display = 'block';
                        } else {
                            suggestionsBox.innerHTML = '';
                            suggestionsBox.style.display = 'none';
                        }
                    })
                    .catch(err => console.error('Search AJAX Error:', err));
            }, 250);
        });
    }
});


// Cart
document.addEventListener('DOMContentLoaded', function () {
    document.addEventListener('click', function (e) {
        const button = e.target.closest('.add-to-cart-btn');
        if (!button) return;

        e.preventDefault();

        const form = button.closest('form');
        if (!form) return;

        const productCard = button.closest('.card') || button.closest('.row');
        const productImg = productCard ? productCard.querySelector('img') : null;
        const cartBadge = document.querySelector('#cart-count-badge');

        if (productImg && cartBadge) {
            const imgRect = productImg.getBoundingClientRect();
            const cartRect = cartBadge.getBoundingClientRect();
            const cloneImg = productImg.cloneNode();

            cloneImg.classList.add('flying-product-img');
            cloneImg.style.position = 'fixed';
            cloneImg.style.zIndex = '9999';
            cloneImg.style.top = `${imgRect.top}px`;
            cloneImg.style.left = `${imgRect.left}px`;
            cloneImg.style.width = `${imgRect.width}px`;
            cloneImg.style.height = `${imgRect.height}px`;
            cloneImg.style.transition = 'all 0.8s ease-in-out';
            document.body.appendChild(cloneImg);

            requestAnimationFrame(() => {
                cloneImg.style.top = `${cartRect.top}px`;
                cloneImg.style.left = `${cartRect.left}px`;
                cloneImg.style.width = '20px';
                cloneImg.style.height = '20px';
                cloneImg.style.opacity = '0.1';
            });

            setTimeout(() => { cloneImg.remove(); }, 800);
        }

        const url = form.getAttribute('action');
        const formData = new FormData(form);

        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const liveBadge = document.querySelector('#cart-count-badge');
                    if (liveBadge) {
                        liveBadge.innerText = data.total_items;
                        liveBadge.classList.add('pulse-animation');
                        setTimeout(() => liveBadge.classList.remove('pulse-animation'), 1000);
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


// Shiping and total price
document.addEventListener('DOMContentLoaded', function () {
    const citySelect = document.getElementById('id_city');
    const shippingDisplay = document.getElementById('shipping-cost');
    const totalDisplay = document.getElementById('order-total');
    const productsSubtotalEl = document.getElementById('products-subtotal');

    if (citySelect && shippingDisplay && totalDisplay && productsSubtotalEl) {

        const productsSubtotal = parseFloat(productsSubtotalEl.getAttribute('data-price'));

        const shippingRates = {
            'CAI': 50.00, 'GIZ': 50.00, 'QAL': 55.00,
            'ALX': 60.00, 'GHR': 65.00, 'MNF': 65.00,
            'DKH': 65.00, 'SHR': 65.00, 'BHG': 65.00,
            'KSH': 65.00, 'DMT': 65.00, 'PSD': 65.00,
            'ISM': 65.00, 'SUZ': 65.00, 'FMT': 70.00,
            'BNS': 70.00, 'MIN': 75.00, 'ASY': 80.00,
            'SOH': 85.00, 'QNA': 90.00, 'LXR': 95.00,
            'ASW': 100.00, 'RSE': 100.00, 'WAD': 120.00,
            'MAT': 100.00, 'SIN': 120.00, 'SIS': 120.00
        };

        function updateSummary() {
            const selectedCity = citySelect.value;
            let shippingCost = 0.00;

            if (selectedCity && shippingRates[selectedCity]) {
                shippingCost = shippingRates[selectedCity];
            }

            const finalTotal = productsSubtotal + shippingCost;

            shippingDisplay.textContent = shippingCost.toFixed(2) + ' EGP';
            totalDisplay.textContent = finalTotal.toFixed(2) + ' EGP';
        }

        citySelect.addEventListener('change', updateSummary);
        updateSummary();
    }
});


// Checkout
document.addEventListener("DOMContentLoaded", function () {

    function updateElegantTotal() {
        let subtotalEl = document.getElementById("products-subtotal");
        let subtotal = parseFloat(subtotalEl.getAttribute("data-price")) || 0;

        let couponEl = document.getElementById("coupon-discount-val");
        let discount = 0;
        if (couponEl) {
            discount = parseFloat(couponEl.getAttribute("data-discount")) || 0;
        }

        let shippingEl = document.getElementById("shipping-cost");
        let shipping = parseFloat(shippingEl.innerText) || 0;

        let totalBeforeDiscount = subtotal + shipping;
        let finalTotalWithShipping = subtotal - discount + shipping;

        let orderTotalEl = document.getElementById("order-total");

        if (couponEl) {
            let targetHTML = `
                <div class="text-end">
                    <div class="text-muted text-decoration-line-through" style="font-size: 10pt; margin-bottom: -2px; opacity: 0.7;">
                        ${totalBeforeDiscount.toFixed(2)} EGP
                    </div>
                    <span style="font-size: 15pt; font-weight: bold; color: #0D1321;">
                        ${finalTotalWithShipping.toFixed(2)} EGP
                    </span>
                </div>
            `;
            if (orderTotalEl.innerHTML.trim() !== targetHTML.trim()) {
                orderTotalEl.innerHTML = targetHTML;
            }
        } else {
            let targetHTML = `
                <span style="font-size: 15pt; font-weight: bold; color: #0D1321;">
                    ${finalTotalWithShipping.toFixed(2)} EGP
                </span>
            `;
            if (orderTotalEl.innerHTML.trim() !== targetHTML.trim()) {
                orderTotalEl.innerHTML = targetHTML;
            }
        }
    }

    updateElegantTotal();

    let shippingCostEl = document.getElementById("shipping-cost");
    if (shippingCostEl) {
        let observer = new MutationObserver(function (mutations) {
            updateElegantTotal();
        });

        observer.observe(shippingCostEl, { childList: true, characterData: true, subtree: true });
    }

    let citySelect = document.querySelector(".checkout-form-fields select");
    if (citySelect) {
        citySelect.addEventListener("change", function () {
            setTimeout(updateElegantTotal, 150);
        });
    }
});


// Active Buttons
$(document).ready(function () {
    function updateActiveButton() {
        const urlParams = new URLSearchParams(window.location.search);
        const category = urlParams.get('category');
        const collection = urlParams.get('collection');
        const slug = urlParams.get('category') || urlParams.get('collection');

        if (slug) {
            $('.category-btn').removeClass('active');
            $(`.category-btn[data-slug="${slug}"]`).addClass('active');
        }
    }

    updateActiveButton();

    $(document).on('click', '.category-btn', function (e) {
        $('.category-btn').removeClass('active');
        $(this).addClass('active');
    });
});

