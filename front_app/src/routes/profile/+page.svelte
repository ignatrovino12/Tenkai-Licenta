<svelte:head>
	<link  href="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/2.0.0-alpha.2/cropper.css" rel="stylesheet">
	<script src="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/2.0.0-alpha.2/cropper.min.js"></script>
</svelte:head>



<script lang="ts">
    import { onMount } from 'svelte';
    import Cropper from 'cropperjs';
  
    function getRoundedCanvas(sourceCanvas: HTMLCanvasElement, size:number): HTMLCanvasElement {
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
      const image = document.getElementById('image');
      const button = document.getElementById('button');
      const result = document.getElementById('result');
      let croppable = false;
  
      if (image instanceof HTMLImageElement) {
        const cropper = new Cropper(image, {
          aspectRatio: 1,
          viewMode: 1,
          ready: function () {
            croppable = true;
          },
        });
  
        if (button) {
          button.onclick = function () {
            if (!croppable) {
              return;
            }
  
            // Crop
            const croppedCanvas = cropper.getCroppedCanvas();
  
            // Round
            const fixedSize = 200;
            const roundedCanvas = getRoundedCanvas(croppedCanvas,fixedSize);
  
            // Show
            const roundedImage = document.createElement('img');
            roundedImage.src = roundedCanvas.toDataURL();
            roundedImage.style.borderRadius = '50%'; 
            if (result) {
              result.innerHTML = '';
              result.appendChild(roundedImage);
            }
          };
        } else {
          console.error('Element with id "button" is not found.');
        }
      } else {
        console.error('Element with id "image" is not found or not an HTMLImageElement.');
      }
    });
  </script>
  
  <div class="container">
    <h1>Crop a round image</h1>
    <h3>Image</h3>
    <div>
      <img id="image" src="gojo.avif" alt="">
    </div>
    <h3>Result</h3>
    <p>
      <button type="button" id="button">Crop</button>
    </p>
    <div id="result"></div>
  </div>
  
