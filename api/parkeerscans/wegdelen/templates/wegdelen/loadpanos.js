

var pano_links = [

  {% for vak in vakken %}

    [{{vak.id}}, "https://api.data.amsterdam.nl/panorama/thumbnail/?lat={{vak.point.y}}&lon={{vak.point.x}}&horizon=0.8&radius=8"],

  {% endfor %}

];



document.addEventListener("DOMContentLoaded", function(event) {
    //load panorama images
    //for(var i=0; i <
});
