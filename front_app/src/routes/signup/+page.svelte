<script>
  let username = "";
  let password = "";
  let password_verify = "";
  let email = "";
  let error = "";
  let errorMessage = "";
  let errorKey = 0;
  import { SERVER_URL,fetchProfilePicture,removeCookie } from "../../lib/utils";
  import "../../app.css";
  import { fade } from 'svelte/transition';

  async function handleSubmit() {
    const formData = {
      username: username,
      password: password,
      password_verify: password_verify,
      email: email,
    };

    try {
      const response = await fetch(`${SERVER_URL}/signup/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const data = await response.json();
        const csrfToken = data.csrf_token;
        document.cookie = `csrftoken=${csrfToken}; path=/;`;
        document.cookie = `username=${username}; path=/;`;

        // save in session storage the image for current user
        const profilePictureData = await fetchProfilePicture("start");
        const profilePicture = profilePictureData.profile_picture;
        sessionStorage.setItem('profile_picture', profilePicture);
        removeCookie('profile_picture')

        window.location.href = "/home"; // Redirect to home if succesfull
      } else {
        const data = await response.json();
        errorMessage = data.message;
        errorKey++;
      }
    } catch (error) {
      console.error("There was a problem with the fetch operation:", error);
    }
  }


  async function handleGoogleLogin() {
    window.location.href = 'https://vladar34.xyz/accounts/google/login/';
  }
</script>

<svelte:head>
  <title>Sign up</title>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
</svelte:head>

<div
  class="min-h-screen flex items-center justify-center bg-gradient-to-r from-cyan-400 to-green-400"
>
  <div
    class="bg-white rounded-lg shadow-md w-full max-w-2xl flex overflow-hidden h-[600px]"
  >
    <div class="w-full p-8 md:p-12 lg:p-16 flex flex-col justify-center">
      <h1 class="text-3xl font-bold mb-8 text-gray-900 text-center">
        Create an account
      </h1>
    {#if errorMessage}
      {#key errorKey}
      <p class="text-red-500 mb-4" in:fade={{delay:300}}  out:fade={{duration: 0}} >{errorMessage}</p>
      {/key}
    {/if}
      <form on:submit|preventDefault={handleSubmit}>
        <div class="mb-4">
          <label class="block text-gray-700 mb-2" for="username"
            >Username:</label
          >
          <input
            type="text"
            id="username"
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400"
            bind:value={username}
            required
          />
        </div>
        <div class="mb-4">
          <label class="block text-gray-700 mb-2" for="email">Email:</label>
          <input
            type="email"
            id="email"
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400"
            bind:value={email}
            required
          />
        </div>
        <div class="mb-4">
          <label class="block text-gray-700 mb-2" for="password"
            >Password:</label
          >
          <input
            type="password"
            id="password"
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400"
            bind:value={password}
            required
          />
        </div>
        <div class="mb-4">
          <label class="block text-gray-700 mb-2" for="password_verify"
            >Verify Password:</label
          >
          <input
            type="password"
            id="password_verify"
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400"
            bind:value={password_verify}
            required
          />
        </div>
        {#if error}
          <p>{error}</p>
        {/if}
        <button
          type="submit"
          class="w-full bg-indigo-500 text-white py-2 rounded-lg hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-400"
        >
          Sign Up
        </button>
        <button
        type="button"
        class="w-full bg-red-500 text-white py-2 rounded-lg hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-400 mt-4"
        on:click={handleGoogleLogin}
      >
        Sign Up with Google
      </form>
      <div class="mt-6 text-center">
        <p class="text-gray-600">
          Already made an account? <a
            href="/login"
            class="text-blue-500 hover:underline">Login here!</a
          >
        </p>
      </div>
    </div>
  </div>
</div>
