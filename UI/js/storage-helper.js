CHECKED_CLASS = 'checked'
ROW_ACTIVE_CLASS = 'active'
// Row 

$('.client .main .table-side .table-box table tbody tr').click(function(){
    $('.client .main .table-side .table-box table tbody tr').removeClass(ROW_ACTIVE_CLASS)
    $(this).addClass(ROW_ACTIVE_CLASS)
    getDataFormValuesWhenClick(this)
})

// Dataform
initDataForm()
$('.storage.dataform .status-box').on('click', function(){
    $('.storage.dataform .status-box').removeClass(CHECKED_CLASS);
    $(this).addClass(CHECKED_CLASS)
})

// If created, reset means init  
// If updated, reset means backward, cancel means init
$('.storage.dataform .form-btn-group .reset').on('click',function(){
    initDataForm()
})

function initDataForm(){
    $('input[name=domain_name]').val('')
    $('input[name=ip_address]').val('')
    $('.status-box').removeClass(CHECKED_CLASS)
    $('.status-box.on').addClass(CHECKED_CLASS)
    $('.created_date').val(new Date().toLocaleDateString('vi').slice(0,10))
    $('.hoster').val($('.user .name').text())
}
function getDataFormValuesWhenClick(row){
    const items = $(row).children()
    let index = $(items[0]).text()
    let domainname = $(items[1]).text()
    let ipaddress = $(items[2]).text()
    let hoster = $(items[3]).text()
    let status = $($(items[4]).children()[0]).text().toLowerCase()
    let createddate = $(items[5]).text()
    $('input[name=domain_name]').val(domainname)
    $('input[name=ip_address]').val(ipaddress)
    
    if( status === 'on'){
        $('.status-box').removeClass(CHECKED_CLASS)
        $('input[value=1]').attr('checked','checked')
        $('input[value=0]').removeAttr('checked')
    }else{
        $('.status-box').removeClass(CHECKED_CLASS)
        $('input[value=0]').attr('checked','checked')
        $('input[value=1]').removeAttr('checked')
    }
    $(`.status-box.${status}`).addClass(CHECKED_CLASS)
    $('.created_date').val(createddate)
    $('.hoster').val(hoster)
}
