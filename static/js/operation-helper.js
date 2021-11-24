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

// $('.typing-form').on('mouseover', function(){
//     $('.files-form').addClass('blur-screen')
//     $(this).removeClass('blur-screen')
// })
// $('.files-form').on('mouseover', function(){
//     $('.typing-form').addClass('blur-screen')
//     $(this).removeClass('blur-screen')
// })