<script
  src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
  integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
  lang="ts"
>
  import "../../app.css";
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
    redirectToUserProfile,
    handleUpVote,
    get_cookie,
    handleCommentButton,
    deleteComment,
    fetchProfilePicture,
    timeAgo,
  } from "../../lib/utils";
  import { find_closest_waypoint, update_map } from "../../lib/gpx_utils";
  import type { Waypoint_upload } from "../../lib/gpx_utils";
  import type { User, Video, Upvote, Comment } from "../../lib/utils";

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
  let comments: Comment[];
  let newComment = "";
  let username= "";
  let current_user_picture = "";
  let show_videos= true;

  // search users
  let name = "";
  let order_by = "nr_videos";
  let is_ascending = false;
  let user_data: User[];

  // search videos
  let video_name = "";
  let order_by_video = "time";
  let is_ascending_video = false;
  let time_period = "";
  let videos: Video[];
  let upvotes: Upvote[];
  
  

  onMount(async () => {
    username = get_cookie("username");
    const csrfToken =get_cookie('csrftoken');
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

  async function handleDownload(video_user: string) {
    const { username, csrfToken } = get_cookie_values();

    try {
      const { cloud_videoUrl, comments_received } = await downloadVideo(
        videoName,
        video_user,
      );

      // video
      if (cloud_videoUrl) {
        document.getElementById("video")?.setAttribute("src", cloud_videoUrl);

        waypoints = await loadGPXData(video_user, csrfToken, videoName);

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
              video_user: video_user,
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
    video_user: string,
    csrfToken: string,
    videoName: string,
  ) {
    const L = await import("leaflet");
    const username  = get_cookie("username");

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
        video_user: video_user,
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

  async function handleUsersSubmit(event: Event) {
    event.preventDefault();
    const { username, csrfToken } = get_cookie_values();
    const response = await fetch(`${SERVER_URL}/display_search_users/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        csrf_token: csrfToken,
        name,
        order_by,
        is_ascending,
      }),
    });
    if (response.ok) {
      const data = await response.json();
      user_data = data;
      show_videos = false;
    } else {
      console.error("Failed to search users");
    }
  }

  async function handleVideosSubmit(event: Event) {
    event.preventDefault();
    const { username, csrfToken } = get_cookie_values();
    const response = await fetch(`${SERVER_URL}/display_search_videos/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        csrf_token: csrfToken,
        video_name,
        order_by: order_by_video,
        is_ascending: is_ascending_video,
        time_period,
      }),
    });
    if (response.ok) {
      const data = await response.json();
      videos = data.videos;
      upvotes = data.upvotes;
      show_videos = true;
      // console.log(videos)
      // console.log(upvotes)
    } else {
      console.error("Failed to search users");
    }
  }

  function no_keypress() {}

  function selectVideoName(name: string, video_user: string) {
    videoName = name;
    handleDownload(video_user);
  }

  async function handleUpVoteClick(video: Video, videoUser: string) {
  try {
    const videoName = video.video_name;
    const success = await handleUpVote(videoName, videoUser);
    if (success) {
      const videoIndex = videos.findIndex((v) => v.video_name === videoName);
      const existingUpvoteIndex = upvotes.findIndex(
        (upvote: Upvote) => upvote.video_name === videoName,
      );
      if (existingUpvoteIndex !== -1) {
        // exista deja
        videos[videoIndex] = {...videos[videoIndex], nr_likes: videos[videoIndex].nr_likes - 1};
        upvotes = [...upvotes.slice(0, existingUpvoteIndex), ...upvotes.slice(existingUpvoteIndex + 1)];
      } else {
        // nu exista
        videos[videoIndex] = {...videos[videoIndex], nr_likes: videos[videoIndex].nr_likes + 1};
        upvotes = [...upvotes, { video_name: videoName }];
      }
    } else {
      console.error("Failed to upvote.");
    }
  } catch (error) {
    console.error("Error upvoting:", error);
  }
}


  function isUpvoted(videoName: string) {
    return upvotes.some((upvote: Upvote) => upvote.video_name === videoName);
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
</script>

<svelte:head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Tenkai</title>
  <link
    rel="stylesheet"
    href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
    integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
    crossorigin=""
  />
</svelte:head>

<!-- Taskbar -->
<button on:click={logout_user}>Logout</button>
<button on:click={redirectToHome}>Home</button>
<button on:click={redirectToProfile}>Profile</button>
<button on:click={redirectToUpload}>Upload</button>
<button on:click={redirectToLogin}>Login</button>
<button on:click={redirectToSignUp}>Sign up</button>

<h2>Home page</h2>

<!-- Search for users -->
<h3>Search users</h3>
<form on:submit={handleUsersSubmit}>
  <label for="name">Name:</label>
  <input type="text" id="name" bind:value={name} />

  <label for="order_by">Order By:</label>
  <select id="order_by" bind:value={order_by}>
    <option value="nr_videos">Number of Videos</option>
    <option value="nr_upvotes">Number of Upvotes</option>
  </select>

  <div>
    <label>
      <input type="radio" bind:group={is_ascending} value={true} /> Ascending
    </label>
    <label>
      <input type="radio" bind:group={is_ascending} value={false} /> Descending
    </label>
  </div>

  <button type="submit">Search</button>
</form>

<!-- Search for videos -->
<h3>Search videos</h3>
<form on:submit|preventDefault={handleVideosSubmit}>
  <label for="video_name">Video Name</label>
  <input id="video_name" type="text" bind:value={video_name} />

  <label for="order_by_video">Order By</label>
  <select id="order_by_video" bind:value={order_by_video}>
    <option value="time">Time</option>
    <option value="nr_upvotes">Number of Upvotes</option>
  </select>

  <div>
    <label>
      <input type="radio" bind:group={is_ascending_video} value={true} /> Ascending
    </label>
    <label>
      <input type="radio" bind:group={is_ascending_video} value={false} /> Descending
    </label>
  </div>

  <label for="time_period">Time Period</label>
  <select id="time_period" bind:value={time_period}>
    <option value="">All time</option>
    <option value="today">Today</option>
    <option value="last_week">Last Week</option>
    <option value="last_month">Last Month</option>
    <option value="last_year">Last Year</option>
  </select>

  <button type="submit">Search</button>
</form>

<!-- Display users -->
{#if user_data && !show_videos}
  <h3>Users</h3>
  {#each user_data as user, index}
    <div>
      <div
        role="button"
        tabindex="0"
        on:click={() => redirectToUserProfile(user.name)}
        on:keypress={no_keypress}
        style="cursor: pointer; max-width: 250px;"
      >
        <img
          src={user.image_link}
          alt={user.name}
          style="width: 50px; height: 50px; display: inline-block; vertical-align: middle;"
        />
        <h3 style="display: inline-block; vertical-align: middle;">
          {user.name}
        </h3>
      </div>
      <p>Videos: {user.nr_videos} Upvotes: {user.nr_upvotes}</p>
    </div>
  {/each}
{/if}

<!-- Display Videos -->
<div>

  {#if videos && upvotes && videos.length > 0 && show_videos}
  <h3>Videos:</h3>
    <ul>
      {#each videos as video}
        <li>
          <div
            role="button"
            tabindex="0"
            on:click={() => redirectToUserProfile(video.username)}
            on:keypress={no_keypress}
            style="cursor: pointer; max-width: 250px;"
          >
            <img
              src={video.image_link}
              alt={video.username}
              style="width: 50px; height: 50px; display: inline-block; vertical-align: middle;"
            />
            <h3 style="display: inline-block; vertical-align: middle;">
              {video.username}
            </h3>
          </div>
          <p>Video name: {video.video_name.replace(".mp4", "")}</p>
          <p>Description: {video.description}</p>
          <p>Number of upvotes: {video.nr_likes}</p>
          <p>Country: {video.country ? video.country : "Unknown"}</p>
          <p>City: {video.city ? video.city : "Unknown"}</p>
          <button
            on:click={() => selectVideoName(video.video_name, video.username)}
            >Select</button
          >
          <button
            on:click={() => handleUpVoteClick(video, video.username)}
            class:selected={upvotes.some(
              (upvote) => upvote.video_name === video.video_name,
            )}
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
  {/if}
</div>

<!-- Map and Video -->
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
