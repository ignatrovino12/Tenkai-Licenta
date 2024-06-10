<script lang="ts">
  // IMPORTS
  import { onMount } from "svelte";
  import {
    get_cookie_values,
    logout_user,
    SERVER_URL,
    downloadVideo,
    redirectToHome,
    redirectToLogin,
    redirectToSignUp,
    redirectToProfile,
    redirectToUpload,
    handleCommentButton,
    timeAgo,
    fetchProfilePicture,
    get_cookie,
    deleteComment,
    handleUpVote,
  } from "../../../lib/utils";
  import { find_closest_waypoint, update_map } from "../../../lib/gpx_utils";
  import type { Waypoint_upload } from "../../../lib/gpx_utils";
  import type { Comment, Upvote,Video  } from "../../../lib/utils";
  import "../../../app.css";

  let waypoints: Waypoint_upload[] = [];
  let map: L.Map;
  let polyline: L.Polyline;
  let captionsUrl = "/captions.vtt";
  let cloud_videoUrl = "";
  let video: HTMLVideoElement;
  let noWaypointsMarker: any;
  let lastWaypoint: Waypoint_upload;
  let speed = 0;
  let country = "";
  let city = "";
  let comments: Comment[];
  let newComment = "";
  let current_user_picture = "";
  let username = "";

  // data from server
  /** @type {import('./$types').PageData} */
  export let data;
  const userData = data.user;

  // set selected video
  let videoName: string = "";

  function selectVideoName(name: string) {
    videoName = name;
    handleDownload();
  }

  onMount(async () => {
    username = get_cookie("username");
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
          if (waypoints && waypoints.length > 0) {
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
            updateInfo(city, country, speed);
          }
        };

        intervalId = setInterval(updateMapFunction, updateInterval);
      });

      video.addEventListener("timeupdate", () => {
        isPlaying = true;
        const updateInterval = 200;

        const updateMapFunction = async () => {
          if (!isPlaying) return;

          const currentTime = video.currentTime;
          if (waypoints && waypoints.length > 0) {
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

  async function handleDownload() {
    const { username, csrfToken } = get_cookie_values();

    try {
      const { cloud_videoUrl, comments_received } = await downloadVideo(
        videoName,
        userData.username,
      );

      // video
      if (cloud_videoUrl) {
        document.getElementById("video")?.setAttribute("src", cloud_videoUrl);

        waypoints = await loadGPXData(username, csrfToken, videoName);

        // new speed and waypoints
        if (waypoints) {
          lastWaypoint = waypoints[0];
          speed = 0;
        }

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
              video_user: userData.username,
            }),
          },
        );

        if (LocationResponse.ok) {
          const data = await LocationResponse.json();
          city = data.city;
          country = data.country;
        } else {
          city = "Unknown";
          country = "Unknown";
          updateInfo(city, country, 0);
        }
      }

      // comments
      if (comments_received) {
        comments = comments_received;
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
        video_user: userData.username,
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

  async function handleCommentButtonClick() {
    try {
      const success = await handleCommentButton(newComment, videoName);
      if (success) {
        if (current_user_picture === "") {
          const profilePictureData = await fetchProfilePicture();
          current_user_picture = profilePictureData.profile_picture;
        }

        comments = [
          {
            timestamp: new Date().toISOString(),
            comment: newComment,
            username: username,
            profile_picture: current_user_picture,
          },
          ...comments,
        ];
      } else {
        alert("Failed to submit comment.");
      }

      // Reset the input field after the comment is submitted
      newComment = "";
    } catch (error) {
      console.error("Failed to submit comment:", error);
    }
  }

  async function handleDeleteComment(comment: Comment) {
    const success = await deleteComment(comment);
    if (success) {
      comments = comments.filter((c) => c !== comment);
    } else {
      alert("Failed to delete comment.");
    }
  }

  async function handleUpVoteClick(video: Video, videoUser: string) {
    try {
      const videoName=video.video_name
      const success = await handleUpVote(videoName, videoUser);
      if (success) {
        // console.log("Upvoted successfully.");

        const existingUpvoteIndex = userData.upvotes.findIndex(
          (upvote:Upvote) => upvote.video_name === videoName,
        );
        if (existingUpvoteIndex !== -1) {
          // exista deja
          userData.upvotes.splice(existingUpvoteIndex, 1);
          video.nr_likes--;
        } else {
          // nu exista
          userData.upvotes.push({ video_name: videoName });
          video.nr_likes++;
        }
        userData.upvotes = [...userData.upvotes];
      } else {
        console.error("Failed to upvote.");
      }
    } catch (error) {
      console.error("Error upvoting:", error);
    }
  }

  function isUpvoted(videoName: string) {
    return userData.upvotes.some(
      (upvote: Upvote) => upvote.video_name === videoName,
    );
  }
</script>

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>User profile</title>
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

<div>
  {#if data}
    {#if userData}
      <p>Username: {userData.username}</p>
      {#if userData.image_link}
        <img src={userData.image_link} alt="" />
      {:else}
        <p>User does not have a picture.</p>
      {/if}

      <h2>Videos:</h2>
      {#if userData.videos && userData.videos.length > 0}
        <ul>
          {#each userData.videos as video}
            <li>
              <p>Video name: {video.video_name.replace(".mp4", "")}</p>
              <p>Description: {video.description}</p>
              <p>Number of upvotes: {video.nr_likes}</p>
              <p>Country: {video.country ? video.country : "Unknown"}</p>
              <p>City: {video.city ? video.city : "Unknown"}</p>
              <button on:click={() => selectVideoName(video.video_name)}
                >Select</button
              >
              <button
                on:click={() =>
                  handleUpVoteClick(video, userData.username)}
                class:selected={userData.upvotes.includes(video.video_name)}
              >
                {#if isUpvoted(video.video_name)}
                  <p>Upvoted</p>
                {:else}
                  <p>Upvote</p>
                {/if}
              </button>
            </li>
          {/each}
        </ul>
      {:else}
        <p>No videos available.</p>
      {/if}
    {:else}
      <p>Loading data...</p>
    {/if}
  {/if}
</div>

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

<!-- Display comments -->
{#if comments}
  <h2>Comments:</h2>
  <input
    type="text"
    bind:value={newComment}
    placeholder="Add your comment here"
  />
  <button on:click={handleCommentButtonClick}>Submit Comment</button>
  {#if comments.length > 0}
    <p></p>
    {#each comments as comment}
      <div class="comment">
        <img
          src={comment.profile_picture}
          alt=""
          style="width: 50px; height: 50px; display: inline-block; vertical-align: middle;"
        />
        <p style="display: inline-block; vertical-align: middle;">
          {comment.username} - {timeAgo(comment.timestamp)}
        </p>
        <p>{comment.comment}</p>
        {#if username === comment.username}
          <button on:click={() => handleDeleteComment(comment)}>Delete</button>
        {/if}
      </div>
    {/each}
  {:else}
    <p>No comments available.</p>
  {/if}
{/if}
