# Attribution and External Use

## MassDOT and MBTA

Optional live mode uses data provided by the Massachusetts Department of Transportation, including the MBTA V3 API.

Display this statement wherever live results are shown:

> Transit data provided by the Massachusetts Department of Transportation, including the MBTA V3 API. This independent project is not affiliated with, endorsed by, or certified by MassDOT or the MBTA.

Do not use MassDOT or MBTA logos. Do not claim ownership of their data. Do not make the interface appear official.

## OpenStreetMap

The interactive map must visibly show:

> © OpenStreetMap contributors

The default URL is:

```text
https://tile.openstreetmap.org/{z}/{x}/{y}.png
```

Do not prefetch, bulk-download, scrape, or package community tiles for offline use. Normal browser caching and Referer behavior must remain enabled. For a persistent or higher-traffic deployment, configure a suitable hosted tile provider rather than relying on the community server.

## Leaflet

Leaflet is loaded from a version-pinned CDN and is licensed under BSD 2-Clause. The license notice is reproduced in `THIRD_PARTY_NOTICES.md`.
