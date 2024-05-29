// IMPORTS
import { onDestroy } from 'svelte';

// FUNCTIONS
const SERVER_URL = 'http://127.0.0.1:8000';

function removeCookie(name: string) {
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

function get_cookie_values() {
  const username = get_cookie('username');
  const csrfToken = get_cookie('csrftoken');
  return { username, csrfToken };
}

async function logout_user() {
  const username = get_cookie('username');
  const csrfToken = get_cookie('csrftoken');

  try {
    const response = await fetch(`${SERVER_URL}/logout/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, csrf_token: csrfToken })
    });

    if (response.ok) {
      removeCookie('username');
      removeCookie('csrftoken');
      console.log('Logged out successfully');
      window.location.href = "/login"; // redirect to login
    } else {
      const data = await response.json();
      console.error('Logout failed:', data.message);
    }
  } catch (error: any) {
    console.error('Logout failed:', error.message);
  }
}

function get_cookie(name: string): string {
  const cookieValue = document.cookie
    .split('; ')
    .find(cookie => cookie.startsWith(name))
    ?.split('=')[1];
  return cookieValue ? decodeURIComponent(cookieValue) : '';
}

async function is_logged(username: string, csrfToken: string): Promise<{ success: boolean, message: string }> {
  try {
    const response = await fetch(`${SERVER_URL}/is_logged/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // 'COOKIES': document.cookie
      },
      // credentials: 'include',
      body: JSON.stringify({ username, csrf_token: csrfToken })
    });

    if (response.ok) {
      return await response.json();
    } else {
      window.location.href = "/login";
      const data = await response.json();
      console.error('Logout failed:', data.message);
      throw new Error('Request failed with status ' + response.status);
    }
  } catch (error: any) {
    console.error('Error:', error.message);
    return { success: false, message: 'An error occurred while processing the request' };
  }
}
async function downloadVideo(videoName: string): Promise<{ cloud_videoUrl: string }> {
  const username = get_cookie('username');
  const csrfToken = get_cookie('csrftoken');

  try {
    const response = await fetch(`${SERVER_URL}/download_video/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, csrf_token: csrfToken, video_name: videoName })
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const data = await response.json();
    if (data.success) {
      return {
        cloud_videoUrl: data.video,

      };
    } else {
      console.error('Error:', data.message);
      throw new Error('Failed to get signed URLs');
    }
  } catch (error) {
    console.error('Error fetching signed URLs:', error);
    throw error;
  }
}

// EXPORTS
export { SERVER_URL }
export { get_cookie }
export { get_cookie_values }
export { logout_user }
export { is_logged, downloadVideo}
