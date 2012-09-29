// update is the name of the event that we set in views.py
$(document).bind('serverpush_update', function(event, data) {
	$('#hits').html(data.hits);
});
