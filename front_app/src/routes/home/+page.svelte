<script lang="ts">
    import { onMount } from 'svelte';

onMount(() => {
  // Codul dvs. aici
  function checkCookie(cookieName: string): boolean {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      let cookie = cookies[i].trim();
      if (cookie.startsWith(cookieName + '=')) {
        return true;
      }
    }
    return false;
  }

  function displayCookies() {
    console.log("Cookies:", document.cookie);
  }

  if (checkCookie('csrftoken')) {
    console.log("Cookie-ul 'csrftoken' există!");
  } else {
    console.log("Cookie-ul 'csrftoken' nu există!");
  }

  displayCookies();
});

  </script>
  

<p>This is home</p>