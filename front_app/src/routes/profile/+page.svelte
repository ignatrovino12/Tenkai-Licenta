<script lang="ts">
  import {
    get_cookie_values,
    logout_user,
    is_logged,
    SERVER_URL,
  } from "../../lib/utils";

    import { onMount } from "svelte";
    import Cropper from "cropperjs";
    
    let roundedImage: any;
    let cropperInstance: Cropper | null = null;
    let uploadButton: HTMLButtonElement | null = null;
    
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
      console.log(data.message);
    } else {
      alert("Image upload failed.");
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
  </script>
  
  <svelte:head>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/2.0.0-alpha.2/cropper.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/2.0.0-alpha.2/cropper.min.js"></script>
  </svelte:head>
  
  <div class="container">
    <h1>Change Profile</h1>
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
  