/**
 * ViewModel for CP750 client
 *
 * License: GPL 3.0
 * Author: Roland Tapken <roland@bitarbeiter.net>
 **/
(function() {
	"use strict";

	// Time after that we should try to autoconnect in seconds
	var DEFAULT_AUTOCONNECT_TIMEOUT=10;

	define(['knockout', 'webchannel'], function(ko, webchannel) {
		
		var currentTime = ko.observable(new Date());
		var error = ko.observable();
		var state = ko.observable("unknown");
		var command = ko.observable("");
		var response = ko.observable("");
		var autoconnectTimeout = ko.observable(0);

		// Reset error on state or response change
		ko.computed(function() {
			state();
			response();
			error(undefined);
		});

		var connect = function() {
			webchannel.call(window.cp750bridge.connect).done(state).error(error);
			autoconnectTimeout(DEFAULT_AUTOCONNECT_TIMEOUT);
		};

		state.subscribe(function(s) {
			if (s === 'connected') {
				// Reset autoconnect
				autoconnectTimeout(DEFAULT_AUTOCONNECT_TIMEOUT);
			}
		});

		var disconnect = function() {
			// Disable autoconnect-timeout
			autoconnectTimeout(false);
			webchannel.call(window.cp750bridge.disconnect).done(state).error(error);
		};

		var submit = function() {
			var cmd = command();
			command("");
			response("Executing " + cmd + "...");
			webchannel.call(window.cp750bridge.send, cmd).done(response).error(error);
		};

		// Update state once and every 30 seconds
		webchannel.call(window.cp750bridge.getState).done(state);
		window.setInterval(function() {
			// Update state every 10 seconds
			webchannel.call(window.cp750bridge.getState).done(state).error(function(message) {
				state('disconnected');
				error(message);
			});
		}, 30000);

		window.setInterval(function() {
			// Update current time
			currentTime(new Date());

			// Check if we need to autoconnect
			if (state()  !== 'connected') {
				if (autoconnectTimeout() === 0) {
					connect();
				}
				autoconnectTimeout(autoconnectTimeout() - 1);
			}
		}, 1000);

		return {
			currentTime: ko.pureComputed(currentTime),
			response: ko.pureComputed(response),
			state: ko.pureComputed(state),
			error: ko.pureComputed(error),
			errorLastUpdate: ko.pureComputed(function() { error(); return new Date(); }),
			connected: ko.pureComputed(function() { return state() === 'connected'; }),
			disconnected: ko.pureComputed(function() { return state() !== 'connected'; }),
			autoconnectTimeout: ko.pureComputed(autoconnectTimeout),
			connect: connect,
			disconnect: disconnect,
			command: command,
			submit: submit
		};
	});
})();
