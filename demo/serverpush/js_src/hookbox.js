jsio('from net import connect as jsioConnect');
jsio('from net.protocols.rtjp import RTJPProtocol');

exports.__jsio = jsio.__jsio;
exports.logging = logging;

logger.setLevel(0);

exports.connect = function(url, cookieString) {
	if (!url.match('/$')) {
		url = url + '/';
	}
	var p = new HookBoxProtocol(url, cookieString);
	if (window.WebSocket) {
		jsioConnect(p, 'websocket', {url: url.replace('http://', 'ws://') + 'ws' });
		p.connectionLost = bind(p, '_connectionLost', 'websocket');
	}
	else {
		jsioConnect(p, 'csp', {url: url + 'csp'})
		p.connectionLost = bind(p, '_connectionLost', 'csp');
	}
	return p;
}

HookBoxProtocol = Class([RTJPProtocol], function(supr) {
	// Public api
	this.onOpen = function() { }
	this.onClose = function(err, wasConnected) { }
	this.onError = function(args) { }
	this.onEvent = function(args) {}
	this.init = function(url, cookieString) {
		supr(this, 'init', []);
		this.url = url;
		try {
			this.cookieString = cookieString || document.cookie;
		} catch(e) {
			this.cookieString = "";
		}
		this.connected = false;

		this._publishes = [];
	}

	this.publish = function(channel_name, data) {
		if (this.connected) {
			this.sendFrame('PUBLISH', {payload: JSON.stringify(data)});
		} else {
			this._publishes.push(data);
		}

	}
	
	this.connectionMade = function() {
		logger.debug('connectionMade');
		this.transport.setEncoding('utf8');
		this.sendFrame('CONNECT', {cookie_string: this.cookieString, url: document.location.pathname, GET: document.location.search, timestamp: $('#generated_timestamp').html()});
	}

	this.frameReceived = function(fId, fName, fArgs) {
		switch(fName) {
			case 'CONNECTED':
				this.connected = true;
				while (this._publishes.length) {
					var pub = this._publishes.splice(0, 1)[0];
					this.publish(pub);
				}				
				this.onOpen();
				break;
			case 'EVENT':
				this.onEvent(fArgs);
				break;
		}
	}
	
	this._connectionLost = function(transportName, reason, wasConnected) {
		if (!wasConnected) {
			logger.debug('connectionFailed', transportName)
			if (transportName == 'websocket') {
				logger.debug('retry with csp');
				this.connectionLost = bind(this, '_connectionLost', 'csp');
				jsioConnect(this, 'csp', {url: this.url + 'csp'})
			}
		} else {
			logger.debug('connectionLost');
			this.connected = false;
			this.onClose();
		}
	}

	this.disconnect = function() {
		this.transport.loseConnection();
	}

})

