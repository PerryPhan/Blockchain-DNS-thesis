const SELECTED_CLASS = "selected"

jQuery.fn.exists = function(){ return this.length > 0; }

var node_info_field = [".id-hash", ".time", ".name", ".ipport", ".status"];
var account_info_field = [".id-hash", ".fullname", ".email", ".type", ".time"];


// 

function get_back_node(list) {
  back_node = {};
  for (let i = 0; i < list.length; i++) {
    back_node[list[i]] = $(
      `.common-part .common-info .flex${list[i]} .value .info span`
    ).text();
  }
  return back_node;
}
// NODE 
function set_node_info(obj, list) {
  for (let i = 0; i < list.length; i++) {
    if (list[i] == ".id-hash") {
      $(`.common-info .flex${list[i]} .value`).html(
        `<div class="info animation slidetoLeft"><span>${
          obj[list[i]]
        }</span></div>`
      );
    } else if (list[i] == ".status") {
      if (obj[list[i]].trim().toLowerCase() == "active") {
        $(`.common-info .flex${list[i]} .value`).addClass("green");
        $(`.common-info .flex${list[i]} .value`).removeClass("grey");
        }
      else{
        $(`.common-info .flex${list[i]} .value`).addClass("grey");
      }
      $(`.common-info .flex${list[i]} .value`).html(
        `<div class="info animation goup"><span>${obj[list[i]]}</span></div>`
      );
    } else {
      $(`.common-info .flex${list[i]} .value`).html(
        `<div class="info animation goup"><span>${
          obj[list[i]]
        }</span></div>`
      );
    }
  }
}

function get_node_obj( this_obj ){
  let data = $(this_obj).parent().parent().children(".data");
  let value = $(data).children(".value");
  // Get value
  let id = $(this_obj).text();
  let ip = $(value).children(".ip").text();
  let name = $(value).children(".name").text();
  let port = $(value).children(".port").text();
  let datetime = $(data).children(".datetime").text();
  let status = $(this_obj).next(".status").text();

  obj = {
    ".id-hash": id,
    ".time": datetime,
    ".name": name,
    ".ipport": ip + " : " + port,
    ".status": status,
  };

  return obj
}

// ACCOUNT
function set_account_info(obj, list) {
  for (let i = 0; i < list.length; i++) {
    if (list[i] == ".id-hash") {
      $(`.common-info .flex${list[i]} .value`).html(
        `<div class="info animation slidetoLeft"><span>${
          obj[list[i]]
        }</span></div>`
      );
    } else if (list[i] == ".status") {
      if (obj[list[i]].trim().toLowerCase() == "admin") {
        $(`.common-info .flex${list[i]} .value`).addClass("purple");
        $(`.common-info .flex${list[i]} .value`).removeClass("blue");
        }
      else{
        $(`.common-info .flex${list[i]} .value`).addClass("blue");
        $(`.common-info .flex${list[i]} .value`).removeClass("purple");
      }
      $(`.common-info .flex${list[i]} .value`).html(
        `<div class="info animation goup"><span>${obj[list[i]]}</span></div>`
      );
    } else {
      $(`.common-info .flex${list[i]} .value`).html(
        `<div class="info animation goup"><span>${
          obj[list[i]]
        }</span></div>`
      );
    }
  }
}

function get_account_obj( this_obj ){
  let data = $(this_obj).parent().parent().children(".data");
  let value = $(data).children(".value");
  // Get value
  let id = $(this_obj).text();
  let fullname = $(value).children(".fullname").text();
  let email = $(value).children(".email").text();
  let time = $(value).next().children(".time").text();
  let type = $(this_obj).next(".status").text().trim();

  obj = {
    ".id-hash": id,
    ".time": time,
    ".email": email,
    ".fullname": fullname,
    ".type": type,
  };
  console.log(obj)
  return obj
}

// COMMON
$(".items").on("click", function(){
  $(".items").removeClass(SELECTED_CLASS)
  $(this).addClass(SELECTED_CLASS)
  $(this).children('.id-hash').children('.value')[0].click()
})

// LOOP
function setEventForItems( classname , list , getFunc , setFunc ){
  console.log("SET EVENT FOR ",classname)
  
  let back_node = get_back_node(list);
  let info_part_h4 = $(`.${classname}-info-part h4`);
  let SELECTED = `Selected ${classname} information`;
  let THIS = `This ${classname} Information`;
  
  info_part_h4.text(THIS);
  $(`.${classname}-info-part .back-node`).hide()

  $(`.items.${classname} .id-hash .value`).on("click", function () {
    set_node_info(getFunc(this), list);
    $(`.${classname}-info-part .back-node`).show()  
    info_part_h4.text(SELECTED);
  });
  
  $(`.${classname}-info-part .back-node`).on("click", function () {
    info_part_h4.text(THIS);
    setFunc(back_node, list);
    $('.items').removeClass('selected')
    $(this).hide()
  });

}


if ( $('.items.node').exists() )
setEventForItems('node', node_info_field, get_node_obj , set_node_info)
if ( $('.items.account').exists() )
setEventForItems('account', account_info_field, get_account_obj, set_account_info)

