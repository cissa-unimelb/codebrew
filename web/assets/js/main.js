/*
	Archetype by Pixelarity
	pixelarity.com @pixelarity
	License: pixelarity.com/license
*/

(function($) {

	skel.breakpoints({
		xlarge:	'(max-width: 1680px)',
		large:	'(max-width: 1280px)',
		medium:	'(max-width: 980px)',
		small:	'(max-width: 736px)',
		xsmall:	'(max-width: 480px)'
	});

	/*var height = window.innerHeight;
	var width = window.innerWidth;
	var timelineOffset = $("#timeline-section").offset();
	var timelineHeight = $("#timeline-outer-wrapper").height();
	//var timelineWidth = $("#timeline-outer-wrapper").width();
	var timelineWidth = $("#timeline-actual").width();

	calTimelineTitleTop = function(){
		if(width > 1280){
			return "6.5em";
		}
		return "5em";
	}
	calTimelineTop = function(){
		if(width > 1280){
			return "8.5em";
		}
		return "7em";
	}
	calTimelineLeftAfter = function(asInt){
		if(width > 1280){
			return (asInt === true) ? 0 : "0em";
		}
		if(width > 736){
			return (asInt === true) ? 6 : "6em";
		}
		if(width > 480){
			return (asInt === true) ? 4 : "4em";
		}
		return (asInt === true) ? 3 : "3em";
	}

	function px(input) {
		var emSize = parseFloat($("body").css("font-size"));
		return (input / emSize);
	}

	function em(input) {
		var emSize = parseFloat($("body").css("font-size"));
		return (emSize * input);
	}

	updateTimeline = function(){
		var timelineTop = $(window).scrollTop() - timelineOffset.top;
		var percent = timelineTop / (timelineHeight - height);

		if(timelineTop < 0){
			$('#timeline-outer-wrapper > h1').css({
				top: '0',
				position: 'relative',
			});
			$('#timeline').css({
				top: '0',
				left: '0',
				position: 'relative',
			});
			$('#timeline-inner-wrapper').css({
				top: '0',
				left: '0px',
				position: 'relative',
			});
		}else if(timelineTop > timelineHeight - height){
			$('#timeline-outer-wrapper > h1').css({
				top: (timelineHeight - height).toString() + 'px',
				position: 'relative',
			});
			$('#timeline').css({
				top: '0',
				left: (-(timelineWidth - width + em(calTimelineLeftAfter(true)))).toString() + 'px',
				position: 'relative',
			});
			$('#timeline-inner-wrapper').css({
				top: (timelineHeight - height).toString() + 'px',
				left: '0px',
				position: 'relative',
			});
		}else if(timelineTop >= 0 && timelineTop <= timelineHeight){
			$('#timeline-outer-wrapper > h1').css({
				top: calTimelineTitleTop(),
				position: 'fixed',
			});
			$('#timeline').css({
				top: calTimelineTop(),
				left: (-percent * (timelineWidth - width + em(calTimelineLeftAfter(true)))).toString() + 'px',
				position: 'fixed',
			});
		}
	}

	$(window).scroll(function(){
		updateTimeline();
	});

	$(window).resize(function(){
		height = window.innerHeight;
		width = window.innerWidth;
		timelineOffset = $("#timeline-section").offset();
		timelineHeight = $("#timeline-outer-wrapper").height();
		timelineWidth = $("#timeline-actual").width();
	});*/

	$(function() {

		var	$window = $(window),
			$body = $('body'),
			$banner = $('#banner'),
			$header = $('#header');

		// Disable animations/transitions until the page has loaded.
			$body.addClass('is-loading');

			$window.on('load', function() {
				window.setTimeout(function() {
					$body.removeClass('is-loading');
				}, 100);
			});

		// Mobile?
			if (skel.vars.mobile)
				$body.addClass('is-mobile');
			else
				skel
					.on('-medium !medium', function() {
						$body.removeClass('is-mobile');
					})
					.on('+medium', function() {
						$body.addClass('is-mobile');
					});

		// Fix: Placeholder polyfill.
			$('form').placeholder();

		// Prioritize "important" elements on medium.
			skel.on('+medium -medium', function() {
				$.prioritize(
					'.important\\28 medium\\29',
					skel.breakpoint('medium').active
				);
			});

		// Dropdowns.
			$('#nav > ul').dropotron({
				alignment: 'right',
				hideDelay: 400
			});

		// Off-Canvas Navigation.

			// Navigation Panel Toggle.
				$('<a href="#navPanel" class="navPanelToggle"></a>')
					.appendTo($header);

			// Navigation Panel.
				$(
					'<div id="navPanel">' +
						'<nav>' +
							$('#nav').navList() +
						'</nav>' +
						'<a href="#navPanel" class="close"></a>' +
					'</div>'
				)
					.appendTo($body)
					.panel({
						delay: 500,
						hideOnClick: true,
						hideOnSwipe: true,
						resetScroll: true,
						resetForms: true,
						side: 'right'
					});

			// Fix: Remove transitions on WP<10 (poor/buggy performance).
				if (skel.vars.os == 'wp' && skel.vars.osVersion < 10)
					$('#navPanel')
						.css('transition', 'none');

		// Header.
			if (skel.vars.IEVersion < 9)
				$header.removeClass('alt');

			if ($banner.length > 0
			&&	$header.hasClass('alt')) {

				$window.on('resize', function() { $window.trigger('scroll'); });

				$banner.scrollex({
					bottom:		$header.outerHeight() + 5,
					terminate:	function() { $header.removeClass('alt'); },
					enter:		function() { $header.addClass('alt'); },
					leave:		function() { $header.removeClass('alt'); $header.addClass('reveal'); }
				});

			}

	});

})(jQuery);