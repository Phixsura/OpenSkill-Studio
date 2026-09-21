# API Deprecation Policy

## Strategy
1. New version endpoints coexist with old for 6 months
2. Deprecated endpoints return `Deprecation` and `Sunset` headers
3. Clients are notified via webhook events

## Headers
- `Deprecation: true` — endpoint is deprecated
- `Sunset: <date>` — endpoint will be removed after this date
- `Link: <new-url>; rel="successor-version"` — replacement endpoint

## Timeline
- Announce: 3 months before sunset
- Deprecation header: immediately
- Removal: after sunset date
