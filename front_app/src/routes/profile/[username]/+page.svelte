<script lang="ts">
  import { writable } from 'svelte/store';

  // data from server
  /** @type {import('./$types').PageData} */
  export let data;
  const userData =  data.user;

  // set selected video 
  export const videoName = writable('');
  function selectVideoName(name: string) {
    videoName.set(name);
  }

  videoName.subscribe(value => {
    console.log('Selected video name:', value);
  });
</script>

<div>
  {#if data}
    {#if userData}
      <p>Username: {userData.username}</p>
    {#if userData.image_link}
      <!-- Display the image using the signed URL -->
      <img src={userData.image_link} alt="">
    {:else}
      <p>User does not have a picture.</p>
    {/if}
     
    <h2>Posts:</h2>
    {#if userData.videos && userData.videos.length > 0}
      <ul>
        {#each userData.videos as video}
          <li>
            <p>Video name: {video.video_name.replace('.mp4', '')}</p>
            <p>Country: {video.country ? video.country : 'Not found'}</p>
            <p>City: {video.city ? video.city : 'Not found'}</p>
            <button on:click={() => selectVideoName(video.video_name)}>Select</button>
          </li>
        {/each}
      </ul>
    {:else}
      <p>No posts available.</p>
    {/if}
  {:else}
    <p>Loading data...</p>
    {/if}
  {/if}
</div>
