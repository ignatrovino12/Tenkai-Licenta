<script >
	import { navigate } from 'svelte-routing'
	import {redirectToLogin } from '../lib/utils'
	import "../app.css";

	function goToAdminPage() {
	  navigate('http://127.0.0.1:8000/admin/');
	}
</script>

<svelte:head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Tenkai</title>
</svelte:head>

<h1 class="text-4xl ml-4 font-bold mb-4 bg-gradient-to-r from-blue-600 via-green-500 to-indigo-400 inline-block text-transparent bg-clip-text">Welcome to Tenkai</h1>


<p class="mb-4  ml-4 ">Are you an Admin? Click here to log in to your admin account:</p>
<button class=" ml-4  bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mb-4" on:click={goToAdminPage}>Admin</button>

<p class="mb-4  ml-4 ">To main Tenkai website:</p>
<button class=" ml-4  bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" on:click={redirectToLogin}>Login</button>
