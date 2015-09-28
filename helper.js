/*function get(elem) {return document.getElementById(elem);}

get("slider").oninput = function() {
  var val = get("slider").value;
  get("title").style.backgroundColor = "hsl(" + val + ", 20%, 84%)";
  get("about").style.backgroundColor = "hsl(" + val + ", 30%, 76%)";
  get("projects").style.backgroundColor = "hsl(" + val + ", 40%, 68%)";
  get("contact").style.backgroundColor = "hsl(" + val + ", 50%, 60%)";
  get("bg").style.backgroundColor = "hsl(" + val + ", 50%, 60%)";
};*/

$(".project-entry, .project-entry-secondary")
.mouseenter(function() {
  $(this).find(".description").fadeIn();
})
.mouseleave(function() {
  $(this).find(".description").fadeOut();
});

$(".highlight-button")
.mouseenter(function() {
  $(this).css("backgroundColor","white").css("color","#455a64");
})
.mouseleave(function() {
  $(this).css("backgroundColor","transparent").css("color","white");
})