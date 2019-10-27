jQuery(document).ready(function () {
  jQuery('.doc-loader').fadeOut('fast');
});

function getInputs(){
  var place=document.getElementById('input1').value;
  var hours=document.getElementById('input2').value;
  var minutes=document.getElementById('input3').value;
  var time = hours * 3600 + minutes * 60;
  $.getJSON('http://127.0.0.1:5000/_getPlace', {
    city: $('input[name="place"]').val(),
    time_limit: $('input[name="time"]').val()
  }, function(data) {
    1+1;
  });
}
