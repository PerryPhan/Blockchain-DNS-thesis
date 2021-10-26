CHECKED_CLASS = 'checked'
// Dataform
$('.storage.dataform .status-box').on('click', function(){
    $('.storage.dataform .status-box').removeClass(CHECKED_CLASS);
    $(this).addClass(CHECKED_CLASS)
})