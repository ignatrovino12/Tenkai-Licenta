<script
  src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
  integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
  lang="ts"
>
  import { onMount } from "svelte";
  import {
    get_cookie_values,
    logout_user,
    is_logged,
    SERVER_URL,
    downloadVideo,
    redirectToHome,
    redirectToLogin,
    redirectToSignUp,
    redirectToProfile,
    redirectToUpload,
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
  let lastWaypoint: Waypoint_upload;
  let speed = 0;
  let country = "";
  let city = "";

  onMount(async () => {
    const { username, csrfToken } = get_cookie_values();
    const response = await is_logged(username, csrfToken);

    if (typeof window !== "undefined") {
      //gpx window


      //video window
      video = document.getElementById("video") as HTMLVideoElement;

      let intervalId: NodeJS.Timeout | null = null;
      let isPlaying = false;

      video.addEventListener("play", () => {
        isPlaying = true;

        const updateInterval = 200;

        const updateMapFunction = async () => {
          if (!isPlaying) return;

          const currentTime = video.currentTime;
          if (waypoints.length > 0) {
            const currentWaypoint = find_closest_waypoint(
              currentTime,
              waypoints,
            );
            speed = await update_map(
              currentWaypoint,
              map,
              lastWaypoint,
              currentTime,
              speed,
              waypoints[0],
            );
            if (lastWaypoint !== currentWaypoint) {
              lastWaypoint = currentWaypoint;
            }
            // if (speed>1)
            // console.log(speed);
            updateInfo(city, country, speed);
          }
        };

        intervalId = setInterval(updateMapFunction, updateInterval);
      });

      video.addEventListener("pause", () => {
        isPlaying = false;
        if (intervalId) {
          clearInterval(intervalId);
          intervalId = null;
        }
      });
    }
  });

  async function handleDownload(event: Event) {
    const form = event.target as HTMLFormElement;
    videoName = form.videoName.value;
    if (!videoName.endsWith(".mp4")) {
      videoName += ".mp4";
    }
    const { username, csrfToken } = get_cookie_values();

    try {
      const { cloud_videoUrl } = await downloadVideo(videoName,username);

      if (cloud_videoUrl) {
        document.getElementById("video")?.setAttribute("src", cloud_videoUrl);

        waypoints = await loadGPXData(username, csrfToken, videoName);

        // new speed and waypoints
        lastWaypoint = waypoints[0];
        speed = 0;

        // get city and country

        const LocationResponse = await fetch(
          `${SERVER_URL}/display_city_country/`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              username,
              csrf_token: csrfToken,
              video_name: videoName,
              video_user: username,
            }),
          },
        );

        if (LocationResponse.ok) {
          const data = await LocationResponse.json();
          city = data.city;
          country = data.country;

        } else {
          const data = await LocationResponse.json();
          alert(data.message);
        }
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
        video_user: username,
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

  async function updateInfo(city: string, country: string, speed: number) {
    try {
      document.getElementById("speed")!.innerText = `Speed: ${speed} km/h`;
      document.getElementById("city")!.innerText = `City: ${city}`;
      document.getElementById("country")!.innerText = `Country: ${country}`;
    } catch (error) {
      console.error("Failed to update info:", error);
    }
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

<!-- Taskbar -->
<button on:click={logout_user}>Logout</button>
<button on:click={redirectToHome}>Home</button>
<button on:click={redirectToProfile}>Profile</button>
<button on:click={redirectToUpload}>Upload</button>
<button on:click={redirectToLogin}>Login</button>
<button on:click={redirectToSignUp}>Sign up</button>

<h2>Home page</h2>

<form on:submit|preventDefault={handleDownload}>
  <label for="videoName">Video Name:</label>
  <input type="text" id="videoName" name="videoName" required />
  <button type="submit">Upload</button>
</form>

<div id="info" style="display: flex; justify-content: center; gap: 20px;">
  <p id="speed">Speed:</p>
  <p id="city">City:</p>
  <p id="country">Country:</p>
</div>

<div style="display: flex; align-items: stretch; justify-content: center;">
  <div
    id="map"
    style="width: 500px; height: 500px; border: 1px solid #000;"
  ></div>

  <video
    id="video"
    controls
    style="max-width: 600px; height: 500px; background-color:#3b3b3b;"
  >
    <track kind="captions" src={captionsUrl} srclang="en" label="English" />
    {#if cloud_videoUrl}
      <source src={cloud_videoUrl} type="video/mp4" />
      Your browser does not support the video tag.
    {/if}
  </video>
</div>
