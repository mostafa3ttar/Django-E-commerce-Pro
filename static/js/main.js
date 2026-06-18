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

            const productCard = this.closest('.card') || this.closest('.row');
            const productImg = productCard ? productCard.querySelector('img') : null;
            const cartBadge = document.getElementById('cart-count-badge');

            if (productImg && cartBadge) {
                const imgRect = productImg.getBoundingClientRect();
                const cartRect = cartBadge.getBoundingClientRect();

                const cloneImg = productImg.cloneNode();
                cloneImg.classList.add('flying-product-img');
                cloneImg.style.top = `${imgRect.top}px`;
                cloneImg.style.left = `${imgRect.left}px`;
                cloneImg.style.width = `${imgRect.width}px`;
                cloneImg.style.height = `${imgRect.height}px`;

                document.body.appendChild(cloneImg);

                requestAnimationFrame(() => {
                    cloneImg.style.top = `${cartRect.top}px`;
                    cloneImg.style.left = `${cartRect.left}px`;
                    cloneImg.style.width = '20px';
                    cloneImg.style.height = '20px';
                    cloneImg.style.opacity = '0.1';
                });

                setTimeout(() => {
                    cloneImg.remove();
                }, 800);
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
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok');
                    return response.json();
                })
                .then(data => {
                    if (data.status === 'success') {
                        if (cartBadge) {
                            cartBadge.innerText = data.total_items;

                            cartBadge.classList.add('pulse-animation');
                            setTimeout(() => {
                                cartBadge.classList.remove('pulse-animation');
                            }, 1000);
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