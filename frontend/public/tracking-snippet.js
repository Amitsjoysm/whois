/**
 * Visitor Tracker - Company Identification Script
 * 
 * Usage:
 * Add this script to your website's <head> or before </body>:
 * 
 * <script>
 *   (function() {
 *     var apiUrl = 'YOUR_API_URL'; // e.g., 'https://your-domain.com'
 *     var script = document.createElement('script');
 *     script.src = apiUrl + '/tracking-snippet.js';
 *     script.setAttribute('data-api-url', apiUrl);
 *     document.head.appendChild(script);
 *   })();
 * </script>
 */

(function() {
  'use strict';

  // Get API URL from script tag
  var scriptTag = document.querySelector('script[data-api-url]');
  var API_URL = scriptTag ? scriptTag.getAttribute('data-api-url') : 'http://localhost:8001';

  // Function to track visitor
  function trackVisitor() {
    try {
      // Collect client-side data
      var data = {
        user_agent: navigator.userAgent,
        referrer: document.referrer || null,
        page_url: window.location.href,
        // IP will be captured server-side from request
      };

      // Send tracking request
      fetch(API_URL + '/api/track', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })
      .then(function(response) {
        return response.json();
      })
      .then(function(result) {
        console.log('[Visitor Tracker] Tracked:', result);
        
        // Optional: Store visitor ID in sessionStorage
        if (result.visitor_id) {
          sessionStorage.setItem('visitor_tracker_id', result.visitor_id);
        }

        // Optional: Trigger custom event for analytics
        if (typeof window.CustomEvent === 'function') {
          var event = new CustomEvent('visitortracked', {
            detail: {
              company: result.company_name,
              confidence: result.confidence,
              isISP: result.is_isp,
              cached: result.cached
            }
          });
          window.dispatchEvent(event);
        }
      })
      .catch(function(error) {
        console.error('[Visitor Tracker] Error:', error);
      });
    } catch (error) {
      console.error('[Visitor Tracker] Error:', error);
    }
  }

  // Track on page load
  if (document.readyState === 'complete') {
    trackVisitor();
  } else {
    window.addEventListener('load', trackVisitor);
  }

  // Optional: Track on SPA navigation (for React, Vue, etc.)
  var pushState = history.pushState;
  history.pushState = function() {
    pushState.apply(history, arguments);
    trackVisitor();
  };

  // Listen for custom tracking event
  window.visitorTracker = {
    track: trackVisitor,
    version: '1.0.0'
  };

})();
