<script>
  let username = "";
  let password = "";
  let errorMessage = "";
  import { SERVER_URL,fetchProfilePicture } from "../../lib/utils";
  import "../../app.css";
  
  async function handleSubmit() {
    try {
      const response = await fetch(`${SERVER_URL}/login/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        const data = await response.json();
        const csrfToken = data.csrf_token;
        document.cookie = `csrftoken=${csrfToken}; path=/;`;
        document.cookie = `username=${username}; path=/;`;
        
        // save in local storage the image for current user
        const profilePictureData = await fetchProfilePicture("start");
        const profilePicture= profilePictureData.profile_picture;
        sessionStorage.setItem('profile_picture', profilePicture);
        
        window.location.href = "/home"; // Redirect to home if succesfull
      } else {
        const data = await response.json();
        errorMessage = data.message;
      }
    } catch (error) {
      console.error("Connection error:", error);
      errorMessage = "A network error has occurred. Please try again.";
    }
  }
</script>



<svelte:head>
  <title>Login</title> 
  <meta charset="utf-8"> 
  <meta name="viewport" content="width=device-width, initial-scale=1.0"> 
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-gradient-to-r from-cyan-400 to-green-400">
  <div class="bg-white rounded-lg shadow-md w-full max-w-6xl flex overflow-hidden">

    <!-- Left Section with image -->
    <div class="hidden md:block w-1/2 bg-cover bg-center relative" style="background-image: url('landscape.png');height: 600px;">
      <div class="absolute inset-0 bg-teal-100 bg-opacity-50"></div>
      <div class="absolute inset-0 flex flex-col items-center justify-center">
        <h2 class="text-3xl text-indigo-600 font-bold mb-4 text-center outline-black-outline-title">Welcome to Tenkai</h2>
        <p class="text-indigo-600 text-lg text-center outline-black-outline">
          Whether you’re hiking in the mountains, cycling through the city, or exploring unknown territories, 
          Tenkai allows you to capture these moments and share them with the world. Connect with people, discover new places, 
          and embark on a digital adventure like no other.
        </p>
      </div>
    </div>

    
    <!-- Right Section with login form -->
    <div class="w-full md:w-1/2 p-8 md:p-12 lg:p-16 flex flex-col justify-center">
      <h1 class="text-3xl font-bold mb-8 text-gray-900 text-center">Login</h1>
      {#if errorMessage}
        <p class="text-red-500 mb-4">{errorMessage}</p>
      {/if}
      <form on:submit|preventDefault={handleSubmit}>
        <div class="mb-4">
          <label class="block text-gray-700 mb-2" for="username">Username:</label>
          <input type="text" id="username" class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400" bind:value={username} />
        </div>
        <div class="mb-4">
          <label class="block text-gray-700 mb-2" for="password">Password:</label>
          <input type="password" id="password" class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400" bind:value={password} />
        </div>
        <button type="submit" class="w-full bg-indigo-500 text-white py-2 rounded-lg hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-400">
          Login
        </button>
      </form>
      <div class="mt-6 text-center">
        <p class="text-gray-600">Don't have an account yet? <a href="/signup" class="text-blue-500 hover:underline">Sign up here!</a></p>
      </div>
    </div>
  </div>
</div>


