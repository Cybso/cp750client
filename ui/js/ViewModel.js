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
	var INPUT_MODES = [
		{ value: 'dig_1', label: 'Didital 1' },
		{ value: 'dig_2', label: 'Digital 2' },
		{ value: 'dig_3', label: 'Digital 3' },
		{ value: 'dig_4', label: 'Digital 4' },
		{ value: 'analog', label: 'MultiCh/Analog' },
		{ value: 'non_sync', label: 'NonSync' },
		{ value: 'mic', label: 'Mic' },
		{ value: 'last', label: 'Previous' },
	];

	define(['knockout', 'webchannel'], function(ko, webchannel) {
		
		var currentTime = ko.observable(new Date());
		var error = ko.observable();
		var state = ko.observable("unknown");
		var autoconnectTimeout = ko.observable(0);

		var faderValue = ko.observable();
		var inputModeValue = ko.observable();
		var muteValue = ko.observable();
		var versionValue = ko.observable();

		// Reset error on state or response change
		ko.computed(function() {
			state();
			faderValue();
			muteValue();
			versionValue();
			error(undefined);
		});

		var connect = function() {
			webchannel.call(window.cp750bridge.connect).done(state).error(error);
			autoconnectTimeout(DEFAULT_AUTOCONNECT_TIMEOUT);
		};

		/**
		 * Sends a CP750 command. The command string
		 * will be stripped from the value.
		 **/
		var send = function(command, value, callback) {
			webchannel.call(window.cp750bridge.send, "" + command + " " + value)
				.done(function(response) {
					console.log(command, value, response);
					if (response.startsWith(command + ' ')) {
						response = response.substring(command.length + 1);
						callback(response);
					}
				}).error(error);
		};

		/**
		 * Converts the response to int
		 **/
		var sendInt = function(command, value, callback) {
			send(command, value, function(response) {
				callback(parseInt(response));
			});
		};

		var sendBool = function(command, value, callback) {
			send(command, value, function(response) {
				callback(response && response !== '0' ? true : false);
			});
		};

		var loadValues = function() {
			sendBool('cp750.sys.mute', '?', muteValue);
			sendInt('cp750.sys.fader', '?', faderValue);
			send('cp750.sys.input_mode', '?', inputModeValue);
			send('cp750.sysinfo.version', '?', versionValue);
		};

		state.subscribe(function(s) {
			if (s === 'connected') {
				// Reset autoconnect and update values
				autoconnectTimeout(DEFAULT_AUTOCONNECT_TIMEOUT);
				loadValues();
			}
		});

		var disconnect = function() {
			// Disable autoconnect-timeout
			autoconnectTimeout(false);
			webchannel.call(window.cp750bridge.disconnect).done(state).error(error);
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
			} else {
				// Upload values
				loadValues();
			}
		}, 1000);

		// Prepare fader object that has additional methods
		var faderControl = ko.computed({
			read: faderValue,
			write: function(value) {
				value = parseInt(value);
				if (isNaN(value) || value < 0 || value > 100) {
					error('Illegal fader value. Expected [0;100]');
					return;
				}
				sendInt('cp750.sys.fader', value, faderValue);
			}
		});

		faderControl.incValue = function(delta) {
			if (delta === undefined) {
				delta = 1;
			}
			delta = parseInt(delta);
			if (isNaN(delta) || delta < -100 || delta > 100) {
				error('Illegal fader delta value. Expected [-100;100]');
				return;
			}
			sendInt('cp750.ctrl.fader_delta', delta, function() {
				sendInt('cp750.sys.fader', '?', faderValue);
			});
		};
		faderControl.inc = function() { faderControl.incValue(1); };
		faderControl.decValue = function(delta) {
			if (delta === undefined) {
				delta = 1;
			}
			faderControl.inc(-parseInt(delta));
		};
		faderControl.dec = function() { faderControl.decValue(1); };

		// Calculate a color from blue (H=235) to red (H=0)
		faderControl.color = ko.pureComputed(function() {
			var hue = (100 - faderValue()) * 2.35; // 0 (red) .. 235 (blue)
			console.log(faderValue(), hue);
			return 'hsl(' + Math.floor(hue) + ',100%,26%)';
		});

		// Add a write-rate limitted fader
		var rateLimittedFader = ko.observable().extend({
			rateLimit: { timeout: 500, method: "notifyWhenChangesStop" }
		});
		rateLimittedFader.subscribe(faderControl);
		faderControl.withRateLimit = ko.computed({
			read: faderControl,
			write: rateLimittedFader
		});

		// Create inputModeControl
		var inputModeControl = ko.computed({
			read: inputModeValue,
			write: function(value) {
				for (var i = 0; i < INPUT_MODES.length; i+=1) {
					if (INPUT_MODES[i].value === value) {
						send('cp750.sys.input_mode', value, inputModeValue);
						return;
					}
				}
				error('Illegal value for "input mode":' + value);
			}
		});
		inputModeControl.list = ko.pureComputed(function() { return INPUT_MODES; });

		return {
			currentTime: ko.pureComputed(currentTime),
			state: ko.pureComputed(state),
			error: ko.pureComputed(error),
			errorLastUpdate: ko.pureComputed(function() { error(); return new Date(); }),
			connected: ko.pureComputed(function() { return state() === 'connected'; }),
			disconnected: ko.pureComputed(function() { return state() !== 'connected'; }),
			autoconnectTimeout: ko.pureComputed(autoconnectTimeout),
			connect: connect,
			disconnect: disconnect,

			version: ko.computed(versionValue),
			fader: faderControl,
			inputMode: inputModeControl,
			mute: ko.computed({
				read: muteValue,
				write: function(value) {
					sendBool('cp750.sys.mute', value, muteValue);
				}
			}),
		};
	});
})();
