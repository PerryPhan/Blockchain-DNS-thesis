ACTIVE_CLASS = "active"
SELECT_CLASS = "select"
// Aside
// $("#menu-toggler").click(function () {
//   let aside = $(".dashboard .aside");
//   if (aside.hasClass("asideSlidetoRight")) {
//     aside.removeClass("asideSlidetoRight");
//     aside.addClass("asideSlidetoLeft");
//   } else if (aside.hasClass("asideSlidetoLeft")) {
//     aside.removeClass("asideSlidetoLeft");
//     aside.addClass("asideSlidetoRight");
//   } else {
//     aside.addClass("asideSlidetoRight");
//   }
// });

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

// Table Operation Save
// Create one form
// Adding virtual inputs type radio or maybe checkbox for multiple value
// Create submit button on somewhere

// Table Pagination

function disablePaginationATag(id) {
  $(id).attr("href", "#");
}

function enablePaginationATag(id, href) {
  $(id).attr("href", href);
}

function handlePaginationPermission(type) {
  let index = parseInt($(`#span-${type}-index-page`).text());
  let total = parseInt($(`#span-${type}-total-page`).text());

  if (index == 0 || total == 0) {
    disablePaginationATag(`#a-${type}-next`);
    disablePaginationATag(`#a-${type}-previous`);
    return;
  }

  enablePaginationATag(`#a-${type}-previous`, `${type}?page=${index - 1}`);
  enablePaginationATag(`#a-${type}-next`, `${type}?page=${index + 1}`);

  if (index >= total) {
    disablePaginationATag(`#a-${type}-next`);
  } else if (index <= 1) {
    disablePaginationATag(`#a-${type}-previous`);
  }
}
handlePaginationPermission('table');
handlePaginationPermission('storage');
