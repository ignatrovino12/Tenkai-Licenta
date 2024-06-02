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
    downloadVideo,
  } from "../../lib/utils";
  import { find_closest_waypoint, update_map } from "../../lib/gpx_utils";
  import type { Waypoint_upload } from "../../lib/gpx_utils";

  let waypoints: Waypoint_upload[] = [];
  let map: L.Map;
  let polyline: L.Polyline;
  let captionsUrl = "/captions.vtt";
  let videoName = "";
  let cloud_videoUrl = "";
  let video: HTMLVideoElement;
  let noWaypointsMarker: any;

  onMount(async () => {
    const { username, csrfToken } = get_cookie_values();
    const response = await is_logged(username, csrfToken);

    if (typeof window !== "undefined") {
      //gpx window

      //video window
      video = document.getElementById("video") as HTMLVideoElement;

      video.addEventListener("timeupdate", () => {
        const currentTime = video.currentTime;
        if (waypoints.length > 0) {
          const currentWaypoint = find_closest_waypoint(currentTime, waypoints);
          update_map(currentWaypoint, map);
        }
      });
    }
  });

  async function handleDownload(event: Event) {
    const form = event.target as HTMLFormElement;
    videoName = form.videoName.value;
    if (!videoName.endsWith('.mp4')) {
      videoName += '.mp4';
      }
    const { username, csrfToken } = get_cookie_values();

    try {
      const { cloud_videoUrl } = await downloadVideo(videoName);
      // console.log(cloud_videoUrl)

      if (cloud_videoUrl) {
        document.getElementById("video")?.setAttribute("src", cloud_videoUrl);

        waypoints = await loadGPXData(username, csrfToken, videoName);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  }

  async function loadGPXData(
    username: string,
    csrfToken: string,
    videoName: string,
  ) {
    const L = await import("leaflet");

    // Initialize the map if it hasn't been initialized yet
    if (!map) {
      map = L.map("map").setView([51.505, -0.09], 13);

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(map);
    }

    const gpxResponse = await fetch(`${SERVER_URL}/display_gpx/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        csrf_token: csrfToken,
        video_name: videoName,
      }),
    });

    const gpxData = await gpxResponse.json();
    const waypoints = gpxData.waypoints;

    // Remove the existing polyline if it exists
    if (polyline) {
      map.removeLayer(polyline);
    }

    if (gpxData.waypoints && gpxData.waypoints.length > 0) {
      if (noWaypointsMarker) {
        map.removeLayer(noWaypointsMarker);
        noWaypointsMarker = null;
      }

      // Add the new map route
      const latLngs = waypoints.map((point: { lat: number; lng: number }) => [
        point.lat,
        point.lng,
      ]);
      polyline = L.polyline(latLngs, { color: "blue" }).addTo(map);
      map.fitBounds(polyline.getBounds());
    } else {
      console.error("No waypoints found in GPX data.");

      const center = map.getCenter();
      const message = "No waypoints found";

      if (!noWaypointsMarker) {
        noWaypointsMarker = L.marker(center)
          .addTo(map)
          .bindPopup(message)
          .openPopup();
      }
    }

    return waypoints;
  }
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

<form on:submit|preventDefault={handleDownload}>
  <label for="videoName">Video Name:</label>
  <input type="text" id="videoName" name="videoName" required />
  <button type="submit">Upload</button>
</form>

<div
  id="map"
  style="height: 500px; width: 500px; border: 1px solid #000;"
></div>

<video id="video" controls style="width:100%;max-width:600px;">
  <track kind="captions" src={captionsUrl} srclang="en" label="English" />
  {#if cloud_videoUrl}
    <source src={cloud_videoUrl} type="video/mp4" />
    Your browser does not support the video tag.
  {/if}
</video>
