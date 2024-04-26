<h1>Welcome to SvelteKit</h1>
<p>Visit <a href="https://kit.svelte.dev">kit.svelte.dev</a> to read the documentation</p>

<script type="module">
	import { navigate } from 'svelte-routing';

	function goToAdminPage() {
	  navigate('http://127.0.0.1:8000/admin/');
	}
</script>
  
  <button on:click={goToAdminPage}>Admin</button>
