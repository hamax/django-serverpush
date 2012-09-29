$(window).load(function() {
	var s = io.connect('http://' + window.location.hostname + ':8013', {rememberTransport: true, transports: ['websocket', 'xhr-polling', 'htmlfile']});

	s.on('connect', function() {
		s.emit('login', {
			'cookies': document.cookie,
			'url': document.location.pathname,
			'GET': document.location.search,
			'timestamp': $('#generated_timestamp').html()
		});
	});

	s.on('message', function(data) {
		$(document).trigger('serverpush_' + data.name, data.payload);
	});
});
