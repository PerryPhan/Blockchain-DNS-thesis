ACTIVE_CLASS = "active"
SELECT_CLASS = "select"

$("#menu-toggler").click(function () {
  let aside = $(".main .aside");
  console.log(aside)

  if (aside.hasClass("asideSlidetoRight")) {
    aside.removeClass("asideSlidetoRight");
    aside.addClass("asideSlidetoLeft");
  } else if (aside.hasClass("asideSlidetoLeft")) {
    aside.removeClass("asideSlidetoLeft");
    aside.addClass("asideSlidetoRight");
  } else {
    aside.addClass("asideSlidetoRight");
  }
});

$(".tab-title").click(function () {
  if ($(this).hasClass(ACTIVE_CLASS)) return
  $(".tab-title").removeClass(ACTIVE_CLASS);
  $(this).addClass(ACTIVE_CLASS);
  $(this).children('a').trigger("click");
});

$(".sub-tab").click(function () {
  if ($(this).hasClass(SELECT_CLASS)) return
  $(".sub-tab").removeClass(SELECT_CLASS);
  $(this).addClass(SELECT_CLASS);
  $(this).children('a').trigger("click");
});




