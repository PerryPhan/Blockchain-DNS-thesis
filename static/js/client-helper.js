$('#menu-toggler').click(function(){
    let aside = $('.client .aside');
    if( aside.hasClass('asideSlidetoRight') ){
        aside.removeClass('asideSlidetoRight')
        aside.addClass('asideSlidetoLeft')
    }else if( aside.hasClass('asideSlidetoLeft')) {
        aside.removeClass('asideSlidetoLeft')
        aside.addClass('asideSlidetoRight')
    }else{
        aside.addClass('asideSlidetoRight')
    }
    // .toggleClass('hide');
})

$('.tab-title').click( function(){
    $('.tab-title').removeClass('active');
    $(this).addClass('active');
})

