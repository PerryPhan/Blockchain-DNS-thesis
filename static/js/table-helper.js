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

// Table Operation Save 
    // Create one form 
    // Adding virtual inputs type radio or maybe checkbox for multiple value
    // Create submit button on somewhere 

// Table Pagination 

function disablePaginationATag(id){
    $(id).attr('href','#')
}

function enablePaginationATag(id, href){
    $(id).attr('href',href)
}

function handlePaginationPermission(){
    let index = parseInt($('#span-table-index-page').text())
    let total = parseInt($('#span-table-total-page').text())
    
    if ( index == 0 || total == 0 ){
        disablePaginationATag('#a-table-next')
        disablePaginationATag('#a-table-previous')
        return      
    }

    enablePaginationATag('#a-table-previous', `table?page=${index -1}`)
    enablePaginationATag('#a-table-next',`table?page=${index +1}`)

    if ( index >= total ){
        disablePaginationATag('#a-table-next')
    }else if( index <= 1) {
        disablePaginationATag('#a-table-previous')
    }
}
handlePaginationPermission()