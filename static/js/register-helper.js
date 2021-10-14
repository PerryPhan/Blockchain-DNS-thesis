// - CSS Class 
CHECKED_CLASS = 'checked'
BORDER_ERROR_CLASS ='border-error'
// - Error 
function disableError(){
  if($("#input-password").hasClass(BORDER_ERROR_CLASS)) $("#input-password").removeClass(BORDER_ERROR_CLASS)
  if($("#input-repassword").hasClass(BORDER_ERROR_CLASS)) $("#input-repassword").removeClass(BORDER_ERROR_CLASS)
  $("input[type=submit]").removeAttr("disabled");
}

function enableError( className ){
  $(className).addClass(BORDER_ERROR_CLASS)
  $("input[type=submit]").attr('disabled', 'disabled');
}

$(".img-box").click(function () {
  $(".img-box").removeClass(CHECKED_CLASS);
  $(this).addClass(CHECKED_CLASS);
});

$("#input-repassword").on('click',function(){
  let password = $("#input-password").val()
  if(password && $(this).val() !== password){
    enableError(this)
  }
})

$("#input-password").on('click',function(){
  let repassword = $("#input-repassword").val()
  if(repassword && $(this).val() !== repassword){
    enableError(this)
  }
})

$("#input-repassword").on('input',function(e){
  let password = $("#input-password").val()
  if( e.target.value && password && e.target.value !== password){
    enableError(this)
  }else{
    disableError()
  }
})

$("#input-password").on('input',function(e){
  let repassword = $("#input-repassword").val()
  if( e.target.value && repassword && e.target.value !== repassword){
    enableError(this)
  }else{
    disableError()
  }
})


