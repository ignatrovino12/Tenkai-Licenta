<script >
	import { navigate } from 'svelte-routing'
	import {redirectToLogin } from '../lib/utils'

	function goToAdminPage() {
	  navigate('http://127.0.0.1:8000/admin/');
	}
</script>

<h1>Welcome to Tenkai</h1>
  
<button on:click={goToAdminPage}>Admin</button>
<button on:click={redirectToLogin}>Login</button>
