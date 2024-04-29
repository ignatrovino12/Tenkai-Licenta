<script>
    import { onMount } from 'svelte';
    import { logout_user } from '../utils';
    import { get_cookie_values } from "../utils";
    import {is_logged} from "../utils";

onMount(async () => {
  
    console.log("Cookies:", document.cookie);
    const { username, csrfToken } = get_cookie_values();
    const response = await is_logged(username, csrfToken);
  
 
});
  
  </script>
  
<button on:click={logout_user}>Logout</button>
<p>This is home</p>