// Auto Domain
DOMAIN = $('input[name=domain]') ;
SOA_MNAME = $('input[name=soa_mname]') ;
SOA_RNAME = $('input[name=soa_rname]') ;
NS_HOST_1 = $('input[name=ns_host1]') ;
NS_HOST_2 = $('input[name=ns_host2]') ;
A_NAME_1  = $('input[name=a_name_1]') ;
A_NAME_2  = $('input[name=a_name_2]') ;
A_NAME_3  = $('input[name=a_name_3]') ;

// Handling
function checkDomainInput(domain){
    if ( domain != ''){
        SOA_MNAME.val('ns1.'+domain);
        SOA_RNAME.val('admin.'+domain);
        NS_HOST_1.val('ns1.'+domain);
        NS_HOST_2.val('ns2.'+domain);
        A_NAME_1.val('@');
        A_NAME_2.val('@');
        A_NAME_3.val('@');
    }else{
        SOA_MNAME.val('');
        SOA_RNAME.val('');
        NS_HOST_1.val('');
        NS_HOST_2.val('');
        A_NAME_1.val('');
        A_NAME_2.val('');
        A_NAME_3.val('');
    }
}

checkDomainInput(DOMAIN.val())

DOMAIN.on('input',function(e){
    domain = e.target.value;
    checkDomainInput(domain) 
})
var file_name_h5 = $('.file-name h5')
var file_list_ul = $('.file-name ul') 

$('.files-field #file-upload').on('input',function(e){
    file_name_h5.text('File List')
    // Get
    new_file_name_split_list = e.target.value.split('\\');
    new_file_name = new_file_name_split_list[new_file_name_split_list.length -1 ]
    // Set
    file_list_ul.append(`<li>${new_file_name}</li>`)    
})
$('.files-form .submit-field button[type=reset]').on('click',function(){
    file_name_h5.text('Empty')
    file_list_ul.html('')    
})