const SELECTED_NODE = "Selected Node Information";
const THIS_NODE = "This Node Information";

var node_info_part_h4 = $(".node-info-part h4");
var node_info_field = [".id-hash", ".time", ".name", ".ipport", ".status"];
var back_node = get_back_node();

function get_back_node() {
  back_node = {};
  for (let i = 0; i < node_info_field.length; i++) {
    back_node[node_info_field[i]] = $(
      `.node-info .flex${node_info_field[i]} .value .info span`
    ).text();
  }
  return back_node;
}

function set_node_info(obj) {
  for (let i = 0; i < node_info_field.length; i++) {
    if (node_info_field[i] == ".id-hash") {
      $(`.node-info .flex${node_info_field[i]} .value`).html(
        `<div class="info animation slidetoLeft"><span>${
          obj[node_info_field[i]]
        }</span></div>`
      );
    } else if (node_info_field[i] == ".status") {
      if (obj[node_info_field[i]].toLowerCase() == "active") {
        $(`.node-info .flex${node_info_field[i]} .value`).addClass("green");
        $(`.node-info .flex${node_info_field[i]} .value`).addClass("grey");
        }
      else{
        $(`.node-info .flex${node_info_field[i]} .value`).addClass("grey");
      }
      $(`.node-info .flex${node_info_field[i]} .value`).html(
        `<div class="info animation goup"><span>${obj[node_info_field[i]]}</span></div>`
      );
    } else {
      $(`.node-info .flex${node_info_field[i]} .value`).html(
        `<div class="info animation goup"><span>${
          obj[node_info_field[i]]
        }</span></div>`
      );
    }
  }
}

$(".items.node .id-hash .value").on("click", function () {
  let data = $(this).parent().parent().children(".data");
  let value = $(data).children(".value");

  // Get value
  let id = $(this).text();
  let ip = $(value).children(".ip").text();
  let name = $(value).children(".name").text();
  let port = $(value).children(".port").text();
  let datetime = $(data).children(".datetime").text();
  let status = $(this).next(".status").text();
  node_info_part_h4.text(SELECTED_NODE);

  obj = {
    ".id-hash": id,
    ".time": datetime,
    ".name": name,
    ".ipport": ip + " : " + port,
    ".status": status,
  };

  set_node_info(obj);
});

$(".node-info-part .back-node").on("click", function () {
  node_info_part_h4.text(THIS_NODE);
  set_node_info(back_node);
});
