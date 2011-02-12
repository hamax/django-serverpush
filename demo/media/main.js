$(document).ready(function() {
	var conn = hookbox.connect('http://' + window.location.hostname + ':8013');

	conn.onError = function(err) {
		document.body.innerHTML = err.msg;
	}

	conn.onOpen = function() { 
		//connection made \o/
		$('#status').html('1');
	}

	conn.onEvent = function(data) {
		//something happened, we got event notification
		$('#updates').append(JSON.stringify(data) + '<br/>');
		$('#hits').html(data.payload.hits);
	}
});
