export const SERVER_URL = 'http://127.0.0.1:8000'; 

function getCookie(name: string){
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith(name + '='))
      ?.split('=')[1];
  
    return cookieValue;
  }

export { getCookie };