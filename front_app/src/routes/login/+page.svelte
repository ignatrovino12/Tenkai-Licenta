<script>
  let username = "";
  let password = "";
  let errorMessage = "";
  import { SERVER_URL } from "../../lib/utils";
  import { onMount } from "svelte";
  
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

<div>
  <h1>Login</h1>
  {#if errorMessage}
    <p style="color: red;">{errorMessage}</p>
  {/if}

  <form method="POST" on:submit|preventDefault={handleSubmit}>
    <label>
      Username:
      <input type="text" bind:value={username} />
    </label>
    <label>
      Password:
      <input type="password" bind:value={password} />
    </label>
    <button type="submit">Login</button>
  </form>
</div>
