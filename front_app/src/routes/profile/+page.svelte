<script lang="ts">
    import { onMount } from "svelte";
    import Cropper from "cropperjs";
    
    let roundedImage: any;
    let cropperInstance: Cropper | null = null;
    
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
    
    onMount(() => {
      const input = document.getElementById("fileInput");
      const button = document.getElementById("button");
      const result = document.getElementById("result");
      const cropperContainer = document.getElementById("cropper-container");
    
      if (input instanceof HTMLInputElement && button && cropperContainer) {
        input.addEventListener("change", (event) => {
          const file = (event.target as HTMLInputElement).files![0];
          const imageUrl = URL.createObjectURL(file);
    
          if (cropperInstance) {
            cropperInstance.destroy();
          }
    
          cropperContainer.innerHTML = ''; // Clear previous content
    
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
              // Cropper is ready
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
    
            // Update the rounded image src
            roundedImage.src = roundedCanvas.toDataURL();
          };
        });
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
  </div>
  