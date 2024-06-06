<script>
    let username = '';
    let password = '';
    let password_verify = '';
    let email = '';
    let error = '';
    let errorMessage = "";
    import { SERVER_URL } from "../../lib/utils";
  
    async function handleSubmit() {
  
      const formData = {
        username: username,
        password: password,
        password_verify: password_verify,
        email: email
      };
  
      try {
        const response = await fetch(`${SERVER_URL}/signup/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData)
        });
  
        if (response.ok) {
        const data = await response.json();
        const csrfToken = data.csrf_token;
        document.cookie = `csrftoken=${csrfToken}; path=/;`;
        document.cookie = `username=${username}; path=/;`;
        console.log(document.cookie)
        
        window.location.href = "/home"; // Redirect to home if succesfull
      } else {
        const data = await response.json();
        errorMessage = data.message;
      }
   
      } catch (error) {
        console.error('There was a problem with the fetch operation:', error);
      }
    }
  </script>
  
  <div>
    <h1>Sign up</h1>
  {#if errorMessage}
    <p style="color: red;">{errorMessage}</p>
  {/if}

  <form method="POST" on:submit|preventDefault={handleSubmit}>
    <label>
      Username:
      <input type="text" bind:value={username} required />
    </label>
    <label>
      Password:
      <input type="password" bind:value={password} required />
    </label>
    <label>
      Verify Password:
      <input type="password" bind:value={password_verify} required />
    </label>
    <label>
      Email:
      <input type="email" bind:value={email} required />
    </label>
    {#if error}
      <p>{error}</p>
    {/if}
    <button type="submit">Sign Up</button>
  </form>

  </div>

  <div style="display: flex; align-items: center; margin-top: 10px;">
    <p style="margin: 0;">Already made an account?</p>
    <a href="/login" style="color: blue; text-decoration: underline; cursor: pointer; margin-left: 5px;">
      Login here!
    </a>
  </div>
  