$(window).load(function() {
	var s = new io.Socket(window.location.hostname, {port: 8013, rememberTransport: true});
	s.connect();

	s.addEvent('connect', function() {
		s.send({
			'cookies': document.cookie,
			'url': document.location.pathname,
			'GET': document.location.search,
			'timestamp': $('#generated_timestamp').html()
			});
	});

	s.addEvent('message', function(data) {
		$(document).trigger('serverpush_' + data.name, data.payload);
	});
});
