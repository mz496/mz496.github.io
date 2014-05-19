function get(elem) {return document.getElementById(elem);}

get("slider").oninput = function() {
  var val = get("slider").value;
  get("title").style.backgroundColor = "hsl(" + val + ", 20%, 84%)";
  get("about").style.backgroundColor = "hsl(" + val + ", 30%, 76%)";
  get("projects").style.backgroundColor = "hsl(" + val + ", 40%, 68%)";
  get("contact").style.backgroundColor = "hsl(" + val + ", 50%, 60%)";
  get("bg").style.backgroundColor = "hsl(" + val + ", 50%, 60%)";
};