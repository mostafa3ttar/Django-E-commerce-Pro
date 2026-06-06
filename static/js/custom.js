/*global $ */
$(function () {
    'use strict';
    $('.info-list li').click(function () {
        $(this).addClass('selected').siblings('li').removeClass('selected');
        // window.console.log($(this).data('class'));
        $('.info-content div').hide();
        $('.' + $(this).data('class')).fadeIn();
    });
});

// to get current year
function getYear() {
    var currentDate = new Date();
    var currentYear = currentDate.getFullYear();

    var yearElement = document.querySelector("#displayYear");

    if (yearElement) {
        yearElement.innerHTML = currentYear;
    }
}

getYear();

