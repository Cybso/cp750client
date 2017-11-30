/**
 * Encapsulates a async webchannel request.
 *
 * Usage:
 *    webchannel.call(method[, arguments...]).done(callback)
 **/
(function() {
	"use strict";

	var ERROR_PREFIX = '⚠';

	define(function() {
		function call(method) {
			var args = [];
			for (var i = 1; i < arguments.length; i+=1) {
				args.push(arguments[i]);
			}
			var result, error;
			var listeners = [], errListeners = [];
			args.push(function(value) {
				var i;
				if (typeof value === 'string' && value !== '' && value.charAt(0) === ERROR_PREFIX) {
					error = value.substring(1);
					for (i = 0; i < errListeners.length; i+=1) {
						errListeners[i].call(errListeners[i], error);
					}
				} else {
					result = value;
					for (i = 0; i < listeners.length; i+=1) {
						listeners[i].call(listeners[i], result);
					}
				}
				listeners = undefined;
				errListeners = undefined;
			});
			method.apply(window, args);

			return {
				done: function(listener) {
					if (listeners === undefined) {
						if (error === undefined) {
							listener.call(listener, result);
						}
					} else {
						listeners.push(listener);
					}
					return this;
				},
				error: function(errListener) {
					if (errListeners === undefined) {
						if (error !== undefined) {
							errListener.call(errListener, error);
						}
					} else {
						errListeners.push(errListener);
					}
					return this;
				}
			};
		}

		return {
			call: call
		};
	});
})();

