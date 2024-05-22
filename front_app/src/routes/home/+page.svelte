<script
  lang="ts"
  src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
  integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
>
  import { onMount } from "svelte";
  import {
    get_cookie_values,
    logout_user,
    is_logged,
    SERVER_URL,
  } from "../../lib/utils";
  import { find_closest_waypoint,update_map} from "../../lib/gpx_utils";

  let waypoints = [];
  let videoURL = "/GH012287.MP4";
  let captionsUrl = '/captions.vtt';

  onMount(async () => {
    // console.log("Cookies:", document.cookie);
    const { username, csrfToken } = get_cookie_values();
    const response = await is_logged(username, csrfToken);

    if (typeof window !== "undefined") {
      //gpx window
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

      //video window
      let video = document.getElementById('video') as HTMLVideoElement;

      video.addEventListener("timeupdate", () => {
        const currentTime = video.currentTime;
        const currentWaypoint = find_closest_waypoint(currentTime,waypoints);
        update_map(currentWaypoint,map);
      });
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

<video id="video" controls style="width:100%;max-width:600px;">
  <track kind="captions" src={captionsUrl} srclang="en" label="English">
  {#if videoURL}
    <source src={videoURL} type="video/mp4">
    Your browser does not support the video tag.
  {/if}
</video>


