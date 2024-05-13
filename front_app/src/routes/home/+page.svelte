<script
  lang="ts"
  src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
  integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
>
  import { onMount } from "svelte";
  import { logout_user } from "../utils";
  import { get_cookie_values } from "../utils";
  import { is_logged } from "../utils";
  import { SERVER_URL } from "../utils";
  // import L from 'leaflet';

  let waypoints = [];

  onMount(async () => {
    console.log("Cookies:", document.cookie);
    const { username, csrfToken } = get_cookie_values();
    const response = await is_logged(username, csrfToken);

    if (typeof window !== "undefined") {
      const L = await import("leaflet");

      let map = L.map("map").setView([51.505, -0.09], 13);

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(map);

      const gpxResponse = await fetch(`${SERVER_URL}/display_gpx/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, csrf_token: csrfToken }),
      });

      const gpxData = await gpxResponse.json();
      const waypoints = gpxData.waypoints;

      // add the map route
      const latLngs = waypoints.map((point: { lat: number; lng: number }) => [
        point.lat,
        point.lng,
      ]);
      const polyline = L.polyline(latLngs, { color: "blue" }).addTo(map);
      map.fitBounds(polyline.getBounds());
    }
  });
</script>

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Home</title>
  <link
    rel="stylesheet"
    href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
    integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
    crossorigin=""
  />
</head>

<button on:click={logout_user}>Logout</button>
<p>This is home</p>

<div
  id="map"
  style="height: 500px; width: 500px; border: 1px solid #000;"
></div>
