/**
 * ViewModel for CP750 client
 *
 * License: GPL 3.0
 * Author: Roland Tapken <roland@bitarbeiter.net>
 **/
(function() {
	"use strict";

	define(['knockout', 'webchannel'], function(ko, webchannel) {
		
		var currentTime = ko.observable(new Date());
		window.setInterval(function() {
			currentTime(new Date());
		}, 1000);

		var state = ko.observable("unknown");
		var command = ko.observable("");
		var response = ko.observable("");

		var connect = function() {
			webchannel.call(window.cp750bridge.connect).done(state);
		};

		var disconnect = function() {
			webchannel.call(window.cp750bridge.disconnect).done(state);
		};

		var submit = function() {
			var cmd = command();
			command("");
			response("Executing " + cmd + "...");
			webchannel.call(window.cp750bridge.send, cmd).done(response);
		};

		webchannel.call(window.cp750bridge.getState).done(state);

		return {
			currentTime: ko.pureComputed(currentTime),
			response: ko.pureComputed(response),
			state: ko.pureComputed(state),
			connect: connect,
			disconnect: disconnect,
			command: command,
			submit: submit
		};
	});
})();
