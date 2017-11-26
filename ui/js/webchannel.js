/**
 * Encapsulates a async webchannel request.
 *
 * Usage:
 *    webchannel.call(method[, arguments...]).done(callback)
 **/
(function() {
	"use strict";

	define(function() {
		function call(method) {
			var args = [];
			for (var i = 1; i < arguments.length; i+=1) {
				args.push(arguments[i]);
			}
			var result;
			var listeners = [];
			args.push(function(value) {
				result = value;
				for (var i = 0; i < listeners.length; i+=1) {
					listeners[i].call(listeners[i], result);
				}
				listeners = undefined;
			});
			method.apply(window, args);

			return {
				done: function(listener) {
					if (listeners === undefined) {
						listener.call(listener, result);
					} else {
						listeners.push(listener);
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

