<script lang="ts">
  import {
    get_cookie_values,
    logout_user,
    is_logged,
    SERVER_URL,
    redirectToHome,
    redirectToLogin,
    redirectToSignUp,
    redirectToProfile,
    redirectToCurrentUserProfile,
    redirectToUpload,
    fetchProfilePicture,
    removeCookie,
  } from "../../lib/utils";

  import { onMount } from "svelte";
  import Cropper from "cropperjs";
  import "../../app.css";

  interface Video {
    video_name: string;
    country: string;
    city: string;
  }

  let roundedImage: any;
  let cropperInstance: Cropper | null = null;
  let uploadButton: HTMLButtonElement | null = null;
  let email = "";
  let password = "";
  let confirmPassword = "";
  let oldPassword = "";
  let videos: Video[] = [];
  let profilePicture = "";

  function getRoundedCanvas(
    sourceCanvas: HTMLCanvasElement,
    size: number,
  ): HTMLCanvasElement {
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    if (!context) return canvas;

    const width = size;
    const height = size;

    canvas.width = width;
    canvas.height = height;

    context.imageSmoothingEnabled = true;
    context.drawImage(sourceCanvas, 0, 0, width, height);
    context.globalCompositeOperation = "destination-in";
    context.beginPath();
    context.arc(
      width / 2,
      height / 2,
      Math.min(width, height) / 2,
      0,
      2 * Math.PI,
      true,
    );
    context.fill();

    return canvas;
  }

  async function handleUpload() {
    if (!roundedImage) {
      alert("Please crop the image first.");
      return;
    }
    const { username: username, csrfToken: csrfToken } = get_cookie_values();
    const dataUrl = roundedImage.src;
    const response = await fetch(`${SERVER_URL}/update_picture/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        image: dataUrl,
        username: username,
        csrf_token: csrfToken,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      alert(data.message);

      const profilePictureData = await fetchProfilePicture("start");
      const profilePicture_copy = profilePictureData.profile_picture;
      sessionStorage.setItem("profile_picture", profilePicture_copy);

      profilePicture = profilePicture_copy;
      // removeCookie('profile_picture')
    } else {
      const data = await response.json();
      alert(data.message);
    }
  }

  async function DisplayVideos() {
    const { username, csrfToken } = get_cookie_values();
    try {
      const response = await fetch(`${SERVER_URL}/display_videos_profile/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, csrf_token: csrfToken }),
      });

      if (response.ok) {
        const data = await response.json();
        return data.videos;
      } else {
        console.error("Failed to get videos from user");
        return [];
      }
    } catch (error) {
      console.error("Error fetching videos");
      return [];
    }
  }

  async function deleteVideo(videoName: string) {
    const { username, csrfToken } = get_cookie_values();
    try {
      const response = await fetch(`${SERVER_URL}/delete_video/`, {
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

      if (response.ok) {
        location.reload();
      } else {
        console.error("Failed to delete video");
      }
    } catch (error) {
      console.error("Error deleting video");
    }
  }

  onMount(async () => {
    const { username, csrfToken } = get_cookie_values();
    const response = await is_logged(username, csrfToken);

    const input = document.getElementById("fileInput");
    const button = document.getElementById("button");
    const result = document.getElementById("result");
    const uploadButton = document.getElementById("uploadButton");
    const cropperContainer = document.getElementById("cropper-container");

    const isBrowser = typeof window !== "undefined";

    if (isBrowser) {
      profilePicture = sessionStorage.getItem("profile_picture") || "";
    }

    videos = await DisplayVideos();

    if (
      input instanceof HTMLInputElement &&
      button &&
      cropperContainer &&
      uploadButton
    ) {
      input.addEventListener("change", (event) => {
        const file = (event.target as HTMLInputElement).files![0];
        const imageUrl = URL.createObjectURL(file);

        if (cropperInstance) {
          cropperInstance.destroy();
        }

        cropperContainer.innerHTML = "";
        const image = document.createElement("img");
        image.src = imageUrl;
        image.id = "image";

        // Attach the image to the cropper container
        cropperContainer.appendChild(image);

        // Initialize Cropper
        cropperInstance = new Cropper(image, {
          aspectRatio: 1,
          viewMode: 1,
          movable: true,
          rotatable: true,
          scalable: true,
          zoomable: true,
          ready: function () {},
        });

        button.onclick = function () {
          if (!cropperInstance) {
            return;
          }

          // Crop
          const croppedCanvas = cropperInstance.getCroppedCanvas();

          // Round
          const fixedSize = 200;
          const roundedCanvas = getRoundedCanvas(croppedCanvas, fixedSize);

          // Show
          if (!roundedImage) {
            roundedImage = document.createElement("img");
            roundedImage.style.borderRadius = "50%";
            if (result) {
              result.innerHTML = "";
              result.appendChild(roundedImage);
            }
          }

          roundedImage.src = roundedCanvas.toDataURL();
        };
      });

      uploadButton.addEventListener("click", handleUpload);
    }
  });

  async function handleSubmit() {

    if (oldPassword === "") {
      alert(
        "Please complete the current password field",
      );
      return;
    }

    if (password === "" && confirmPassword === "" && email === "") {
      alert(
        "Please complete at least the email or the password before sending",
      );
      return;
    }

    if (password !== "" || confirmPassword !== "") {
      if (password !== confirmPassword) {
        alert("Passwords do not match");
        return;
      }
    }

    const { username, csrfToken } = get_cookie_values();

    // Submit the form
    const response = await fetch(`${SERVER_URL}/update_credentials/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: username,
        csrf_token: csrfToken,
        email: email,
        password: password,
        old_password: oldPassword,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      alert(data.message);
    } else {
      const data = await response.json();
      alert(data.message);
    }

    email = "";
    password = "";
    confirmPassword = "";
    oldPassword = "";
  }
</script>

<svelte:head>
  <link
    href="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/2.0.0-alpha.2/cropper.css"
    rel="stylesheet"
  />
  <link
  rel="stylesheet"
  href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
/>

  <script
    src="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/2.0.0-alpha.2/cropper.min.js"
  ></script>
  <title>Profile</title>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
</svelte:head>

<!-- Navbar -->

<div
  class="h-screen w-48 bg-gray-800 fixed top-0 left-0 flex flex-col items-center py-4 shadow-lg"
>
  <div class="flex flex-col items-center mt-4">
    <div class="mb-8">
      {#if profilePicture}
        <img
          src={profilePicture}
          alt=""
          class="w-16 h-16 rounded-full border-2 border-white"
        />
      {:else}
        <div class="w-16 h-16 rounded-full border-2 border-white flex"></div>
      {/if}
    </div>
    <button
      class="mb-4 w-full text-white py-2 px-4 rounded hover:bg-gray-700 flex items-center"
      on:click={logout_user}
    >
      <i class="fas fa-sign-out-alt mr-2"></i>Logout
    </button>
    <button
      class="mb-4 w-full text-white py-2 px-4 rounded hover:bg-gray-700 flex items-center"
      on:click={redirectToHome}
    >
      <i class="fas fa-home mr-2"></i>Home
    </button>
    <button
      class="mb-4 w-full text-white py-2 px-4 rounded hover:bg-gray-700 flex items-center"
      on:click={redirectToProfile}
    >
      <i class="fas fa-user mr-2"></i>Profile
    </button>
    <button
      class="mb-4 w-full text-white py-2 px-4 rounded hover:bg-gray-700 flex items-center"
      on:click={redirectToUpload}
    >
      <i class="fas fa-upload mr-2"></i>Upload
    </button>
    <button
      class="mb-4 w-full text-white py-2 px-4 rounded hover:bg-gray-700 flex items-center"
      on:click={redirectToLogin}
    >
      <i class="fas fa-sign-in-alt mr-2"></i>Login
    </button>
    <button
      class="mb-4 w-full text-white py-2 px-4 rounded hover:bg-gray-700 flex items-center"
      on:click={redirectToSignUp}
    >
      <i class="fas fa-user-plus mr-2"></i>Sign up
    </button>
  </div>
  <img
  src="/logo.png"
  alt="Logo"
   class="w-36 h-36 object-contain mt-auto mb-4"
  />
</div>

<!-- Profile -->
<div class="ml-52 mt-8">
  <!-- Public profile link -->
  <h1 class="text-xl font-bold mb-4">Your public profile</h1>
  <button
    class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
    on:click={redirectToCurrentUserProfile}>Your profile</button
  >

  <!-- Change Credentials -->
  <div class="container_credentials mt-8 max-w-64">
    <h1 class="text-xl font-bold mb-4">Change Credentials</h1>

    <form on:submit|preventDefault={handleSubmit} class="space-y-4">
      <label for="oldPassword" class="block">Current Password:</label>
      <input
        type="password"
        id="oldPassword"
        bind:value={oldPassword}
        class="w-64 w-full px-3 py-2 border rounded-md"
      />

      <label for="email" class="block">Email:</label>
      <input
        type="email"
        id="email"
        bind:value={email}
        class=" w-64 w-full px-3 py-2 border rounded-md"
      />

      <label for="password" class="block">New Password:</label>
      <input
        type="password"
        id="password"
        bind:value={password}
        class="w-64 w-full px-3 py-2 border rounded-md"
      />

      <label for="confirmPassword" class="block">Confirm New Password:</label>
      <input
        type="password"
        id="confirmPassword"
        bind:value={confirmPassword}
        class="w-64 w-full px-3 py-2 border rounded-md"
      />

      <div>
        <button
          type="submit"
          class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded w-32"
          >Submit</button
        >
      </div>
    </form>
  </div>

  <!-- Change Profile Picture -->
  <div class="container mt-8">
    <div class="flex flex-col lg:flex-row items-center">
        <div class="lg:w-1/2 pr-4">
            <h1 class="text-xl font-bold mb-4">Change Profile Picture</h1>
            <form>
                <input type="file" id="fileInput" accept="image/*" class="mb-4">
            </form>
            <div id="cropper-container" style="height:300px; width:600px;" class="mb-4 border"></div>
        </div>
        <div class="flex items-center justify-center lg:ml-8 lg:mr-4 my-4 lg:my-0 pt-16">
          <i class="fas fa-arrow-right text-6xl text-gray-500"></i>
      </div>
        <div class="lg:w-1/2 lg:pl-4 lg:ml-4 pt-16 ">
            <h3 class="text-xl font-bold mb-2 lg:mt-0 lg:ml-16 ">&nbsp; Result</h3>
            <div id="result" class="mt-4 mb-4 "></div>
        </div>
    </div>
    <div class="mt-4 flex justify-center">
        <button type="button" id="button" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mr-2">Crop</button>
        <button type="button" id="uploadButton" class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">Upload</button>
    </div>
</div>


<!-- Delete Videos -->
<div class="container_videos    mt-8 p-4 border rounded shadow-lg h-96 overflow-y-scroll" style="width:600px;">
  <h1 class="text-xl font-bold mb-4">Delete videos</h1>
  {#if (videos?.length || 0) > 0}
    <ul class="space-y-4">
      {#each videos as video}
        <li class="flex justify-between items-center p-2 bg-gray-100 rounded">
          <div class="flex-grow max-w-3/4">
            <p class="text-sm break-words container_text ">
            Video Name: {video.video_name.replace(".mp4", "")} - Country: {video.country || "Unknown"}, City: {video.city || "Unknown"}
          </p>
        </div>
          <button
            on:click={() => deleteVideo(video.video_name)}
            class="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded"
          >
            Delete
          </button>
          
        </li>
      {/each}
    </ul>
  {:else}
    <p class="text-gray-500">No videos available.</p>
  {/if}
</div>

</div>
