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
  } from "../../lib/utils";

    import { onMount } from "svelte";
    import Cropper from "cropperjs";
    
    interface Video {
    video_name: string;
    country: string;
    city: string;
  }

    let roundedImage: any;
    let cropperInstance: Cropper | null = null;
    let uploadButton: HTMLButtonElement | null = null;
    let email = '';
    let password = '';
    let confirmPassword = '';
    let oldPassword = '';
    let videos: Video[] = [];
    
    function getRoundedCanvas(
      sourceCanvas: HTMLCanvasElement,
      size: number
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
      context.arc(width / 2, height / 2, Math.min(width, height) / 2, 0, 2 * Math.PI, true);
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
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        image: dataUrl,
        username: username,
        csrf_token: csrfToken,
      })
    });
  
    if (response.ok) {
      const data = await response.json();
      alert(data.message);
    } else {
      const data = await response.json();
      alert(data.message);
    }
  }

  async function DisplayVideos() {
    const { username, csrfToken } = get_cookie_values();
    try {
      const response = await fetch(`${SERVER_URL}/display_videos_profile/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username,csrf_token:csrfToken })
      });

      if (response.ok) {
        const data = await response.json();
        return data.videos;
      } else {
        console.error('Failed to get videos from user');
        return [];
      }
    } catch (error) {
      console.error('Error fetching videos');
      return [];
    }
  }

  async function deleteVideo(videoName: string) {
    const { username, csrfToken } = get_cookie_values();
    try {
      const response = await fetch(`${SERVER_URL}/delete_video/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username,csrf_token:csrfToken, video_name: videoName  })
      });

      if (response.ok) {
        location.reload();
      } else {
        console.error('Failed to delete video');

      }
    } catch (error) {
      console.error('Error deleting video');
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
      videos = await DisplayVideos();
    
      if (input instanceof HTMLInputElement && button && cropperContainer && uploadButton) {
        input.addEventListener("change", (event) => {
          const file = (event.target as HTMLInputElement).files![0];
          const imageUrl = URL.createObjectURL(file);
    
          if (cropperInstance) {
            cropperInstance.destroy();
          }
    
          cropperContainer.innerHTML = ''; 
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
            ready: function () {
    
            },
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

      if ( password==='' && confirmPassword==='' && email===''){
    alert('Please complete at least the email or the password before sending');
    return;
  }
   
    if ( password!=='' || confirmPassword!=='') {
    if (password !== confirmPassword) {
      alert('Passwords do not match');
      return;
    }
  }


    const { username, csrfToken } = get_cookie_values();

    // Submit the form 
    const response = await fetch(`${SERVER_URL}/update_credentials/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        username: username,
        csrf_token: csrfToken,
        email : email,
        password : password,
        old_password : oldPassword,
      })
    });
  
    if (response.ok) {
      const data = await response.json();
      alert(data.message);
    } else {
      const data = await response.json();
      alert(data.message);
    }

  
    email = '';
    password = '';
    confirmPassword = '';
    oldPassword= ''
  }
  </script>
  
  <svelte:head>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/2.0.0-alpha.2/cropper.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/2.0.0-alpha.2/cropper.min.js"></script>
  </svelte:head>
  
  <!-- Taskbar -->
<button on:click={logout_user}>Logout</button>
<button on:click={redirectToHome}>Home</button>
<button on:click={redirectToProfile}>Profile</button>
<button on:click={redirectToUpload}>Upload</button>
<button on:click={redirectToLogin}>Login</button>
<button on:click={redirectToSignUp}>Sign up</button>

<h1>Your public profile</h1>
<button on:click={redirectToCurrentUserProfile}>Your profile</button>

  <div class="container_credentials">
    <h1>Change Credentials</h1>
    
    <form on:submit|preventDefault={handleSubmit}>

      <label for="oldPassword">Current Password:</label><br>
      <input type="password" id="oldPassword" bind:value={oldPassword}><br>

      <label for="email">Email:</label><br>
      <input type="email" id="email" bind:value={email}><br>
      
      <label for="password">New Password:</label><br>
      <input type="password" id="password" bind:value={password}><br>
      
      <label for="confirmPassword">Confirm New Password:</label><br>
      <input type="password" id="confirmPassword" bind:value={confirmPassword}><br>
      
      <button type="submit">Submit</button>
    </form>
  </div>


  <div class="container">
    <h1>Change Profile Picture</h1>
    <form>
      <input type="file" id="fileInput" accept="image/*" />
    </form>
    <div id="cropper-container" style="height:300px; width:600px;"></div>
    <h3>Result</h3>
    <p>
      <button type="button" id="button">Crop</button>
    </p>
    <div id="result"></div>
    <p>
      <button type="button" id="uploadButton">Upload</button>
    </p>
  </div>

  <div class="container_videos">
    <h1>Delete videos</h1>
    {#if videos.length > 0}
      <ul>
        {#each videos as video}
          <li>
            <p>Video Name: {video.video_name.replace('.mp4', '')} - Country: {video.country || 'Unknown'} , City: {video.city || 'Unknown'}</p>
            <button on:click={() => deleteVideo(video.video_name)}>Delete</button>
          </li>
        {/each}
      </ul>
    {:else}
      <p>No videos available.</p>
    {/if}
  </div>
  