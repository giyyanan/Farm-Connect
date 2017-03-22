
var initialize = function()
{
    if(document.getElementById("error"))
    {
        showAlert('error',document.getElementById("error").innerHTML)
    }
    if(document.getElementById("warn"))
    {
        showAlert('warning',document.getElementById("warn").innerHTML)
    }
    if(document.getElementById("info"))
    {
        showAlert('info',document.getElementById("info").innerHTML)
    }
    if(document.getElementById("notify"))
    {
        showAlert('notify',document.getElementById("notify").innerHTML)
    }
}
var  getCurrentLocation = function ()
{
	if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
    } else {
        showAlert("error","Geolocation is not supported by this browser.");
    }

}
var showPosition = function(position) {
   loadMap(position.coords.latitude,position.coords.longitude)
}

var loadMap = function(latitude,longitude){
    var mapCanvas = document.getElementById("address_map");
    var mapOptions = {
        center: new google.maps.LatLng(latitude,longitude), zoom: 15
    }
    var map = new google.maps.Map(mapCanvas, mapOptions);

    var marker = new google.maps.Marker({
        position: new google.maps.LatLng(latitude,longitude),
        map: map,
        title: 'Your Address'
    });
}
var geocodeFromAdress = function(address) {
    var geocoder= new google.maps.Geocoder();
    geocoder.geocode( { 'address': address}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        var latLng = results[0].geometry.location;
        //alert(latLng); //Outputs coordinates, but is for some reason outputted 2nd
        loadMap(latLng.lat(),latLng.lng())
    } else {
        showAlert('error','Co-ordinates could not be fetched for the location. Please enter a valid address');
    }
});
}

var getCookie = function(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var showMap = function(event){
    //alert(event)
}

var searchDemands = function(event)
{
    var valid = true
    var category = document.getElementById("category").value
    var produce = document.getElementById("produce").value

    var gt_quantity = document.getElementById("gt_quantity").value
    var lt_quantity = document.getElementById("lt_quantity").value
    var eq_quantity = document.getElementById("eq_quantity").value

    if(eq_quantity.length != 0 &&(gt_quantity.length != 0 || lt_quantity.length != 0))
    {
        showAlert('warning','If you are specifing a equal to value there is no use in searching with less or greater than')
        valid = false
    }
    var gt_price = document.getElementById("gt_price").value
    var lt_price = document.getElementById("lt_price").value
    var eq_price = document.getElementById("eq_price").value

    if(eq_price.length != 0 &&(gt_price.length != 0 || lt_price.length != 0))
    {
        showAlert('warning','If you are specifing a equal to value there is no use in searching with less or greater than')
        valid = false
    }
    

    if(valid)
    {
       
    csrftoken = getCookie('csrftoken')
       
    $.ajax({
        url:"/search-demands",
        type:"POST",
        headers: { 
            "X-CSRFToken" : csrftoken,
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data:{ "category": category,"produce": produce, "gt_quantity":gt_quantity,"lt_quantity":lt_quantity,"eq_quantity":eq_quantity ,"gt_price":gt_price,"lt_price":lt_price,"eq_price":eq_price},
        //data:{ "category": category, "produce": produce, "gt_quantity":gt_quantity,"lt_quantity":lt_quantity, "eq_quantity":eq_quantity,"gt_price":gt_price,"lt_price":lt_price,"eq_price":eq_price,},
        dataType:"html",
        success : function(result){
            addDemandstoDemandTable(result);
        }
    });
}
}

var addDemandstoDemandTable = function(result)
{

    var temp = document.createElement("div")
    temp.innerHTML = result;
    var container = document.getElementById("demandsTable")
    container.innerHTML = result;
    
    if(result.indexOf('<td>') === -1)
    {
        showAlert('info','no records found')
    }
}

var showAlert = function(type,message)
{
    if(type.length!=0)
    {
        if(type === "error")
        {
            temp = document.getElementById("alert").cloneNode(true)
            temp.getElementsByClassName('alert_message')[0].innerHTML = message
        }
        else if (type==="info")
        {
            temp = document.getElementById("information").cloneNode(true)
            temp.getElementsByClassName('info_message')[0].innerHTML = message
        }
        else if (type==="warning")
        {
            temp = document.getElementById("warning").cloneNode(true)
            temp.getElementsByClassName('warning_message')[0].innerHTML = message
        }
        else if (type==="notify")
        {
            temp = document.getElementById("success").cloneNode(true)
            temp.getElementsByClassName('success_message')[0].innerHTML = message
        }
        temp.style.display = "block";
        document.getElementById("alerts").appendChild(temp);
        (function(temp){setTimeout(function(){temp.getElementsByClassName('close')[0].click()},5000)})(temp);
        temp = "";
        
    }

    
}