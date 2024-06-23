// IMPORTS
import { onDestroy } from 'svelte';
import { derived } from 'svelte/store';

//INTERFACES

interface Comment {
    timestamp: string;  
    comment: string;
    username: string;
    profile_picture: string;
}

interface Upvote {
  video_name:string;
}

interface Video {
  video_name: string, 
  country: string, 
  city: string, 
  nr_likes: number,
  description: string,
  image_link: string,
  username: string,
  timestamp : string,
}

interface User {
  name: string,
  nr_videos: number,
  nr_upvotes : number,
  image_link : string,
}
// FUNCTIONS
const SERVER_URL = 'https://vladar34.xyz/api';


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
async function downloadVideo(videoName: string,videoUser:string): Promise<{ cloud_videoUrl: string, comments_received:Comment[] }> {
  const username = get_cookie('username');
  const csrfToken = get_cookie('csrftoken');

  try {
    const response = await fetch(`${SERVER_URL}/download_video/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, csrf_token: csrfToken, video_name: videoName,video_username:videoUser })
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const data = await response.json();
    if (data.success) {
      return {
        cloud_videoUrl: data.video,
        comments_received: data.comments,

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

type Unsubscribe = () => void;

function watch(expression: () => string, callback: (newValue: string, oldValue?: string) => void) {
  let oldValue: string | undefined = expression();

  const unsubscribe: Unsubscribe = () => {};
  onDestroy(unsubscribe);

  return () => {
      const newValue = expression();
      if (newValue !== oldValue) {
          callback(newValue, oldValue);
          oldValue = newValue;
      }
  };
}

function redirectToHome() {
  window.location.href = '/home'; 
}

function redirectToLogin() {
  window.location.href = '/login'; 
}

function redirectToSignUp() {
  window.location.href = '/signup'; 
}

function redirectToProfile() {
  window.location.href = '/profile'; 
}

function redirectToUpload() {
  window.location.href = '/upload'; 
}

function redirectToCurrentUserProfile() {
  const username = get_cookie('username');
  window.location.href =`/profile/${username}`; 
}


function redirectToUserProfile(username:string) {
  window.location.href =`/profile/${username}`; 
}

function wait(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function handleCommentButton(newComment:string,videoName:string) {
  const { username, csrfToken } = get_cookie_values();

  const NewCommentResponse = await fetch(`${SERVER_URL}/make_comment/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username,
      csrf_token: csrfToken,
      video_name: videoName,
      new_comment: newComment,
    }),
  });

  const data = await NewCommentResponse.json();
  return data.success


}

function timeAgo(timestamp:string) {
  const now = new Date().getTime();
  const date = new Date(timestamp).getTime();
  const seconds = Math.floor((now - date) / 1000);

  let interval = Math.floor(seconds / 31536000);
  
  if (interval >= 1) {
    return `${interval} years ago`;
  }
  interval = Math.floor(seconds / 2592000);
  if (interval >= 1) {
    return `${interval} months ago`;
  }
  interval = Math.floor(seconds / 86400);
  if (interval >= 1) {
    return `${interval} days ago`;
  }
  interval = Math.floor(seconds / 3600);
  if (interval >= 1) {
    return `${interval} hours ago`;
  }
  interval = Math.floor(seconds / 60);
  if (interval >= 1) {
    return `${interval} minutes ago`;
  }
  return `${Math.floor(seconds)} seconds ago`;
}

async function fetchProfilePicture(when:string):Promise<{ profile_picture: string }> {
  try {  
      const { username, csrfToken } = get_cookie_values();
      const response = await fetch(`${SERVER_URL}/display_profile_picture/`, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({ username: username, csrf_token: csrfToken, when}),
      });
      
      if (response.ok) {
          const data = await response.json();
          if (data.success) {

            return { profile_picture: data.profile_picture };
          } else {
              console.error('Failed to fetch profile picture');
          }
      } else {

          console.error('Failed to fetch profile picture');
      }
  } catch (error) {
      console.error('Error fetching profile picture:', error);
  }
  return { profile_picture: "" };
}

async function deleteComment(comment: Comment) {
  try {
    const { username, csrfToken } = get_cookie_values();
    const response = await fetch(`${SERVER_URL}/delete_comment/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username,
        csrf_token: csrfToken,
        timestamp: comment.timestamp,
        comment: comment.comment
      }),
    });
    
    if (response.ok) {
      return true;
    } else {
      console.error('Failed to delete comment:', response.statusText);
      return false;
    }
  } catch (error) {
    console.error('Error deleting comment:', error);
    return false;
  }
}


async function handleUpVote(videoName:string,videoUser:string) {
  try {
    const { username, csrfToken } = get_cookie_values();
    const response = await fetch(`${SERVER_URL}/upload_upvote/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username,
        csrf_token: csrfToken,
        video_name: videoName,
        video_user : videoUser,
      }),
    });

    if (response.ok) {
      return true
    } else {
      console.error('Failed to upvote:', response.statusText);
      return false
    }
  } catch (error) {
    console.error('Error upvoting:', error);
    return false
  }
}

// EXPORTS
export { SERVER_URL,get_cookie, get_cookie_values ,logout_user,wait,timeAgo,deleteComment,handleUpVote,removeCookie }
export { is_logged, downloadVideo,watch,handleCommentButton,fetchProfilePicture}
export {redirectToHome,redirectToLogin,redirectToSignUp,redirectToProfile,redirectToCurrentUserProfile,redirectToUpload,redirectToUserProfile}
export type {Comment,Upvote,Video,User }
