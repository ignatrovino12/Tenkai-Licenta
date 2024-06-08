
import { error } from '@sveltejs/kit';
import {SERVER_URL, get_cookie_values} from "../../../lib/utils"

/** @type {import('./$types').PageServerLoad} */
export async function load({ params }: { params: { username: string} }) {
    const { username} = params;

 
    if (typeof document !== 'undefined') {
   
        const { username: u, csrfToken: token } = get_cookie_values();
        
    
        try {
            const res = await fetch(`${SERVER_URL}/profile/${username}`, {
                method: 'POST', 
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username:u,
                    csrf_token: token,
                    // video_user: username,
                  }),
            });
    
            if (res.ok) {
                const user = await res.json();
                // console.log(user)
                return { user };
            } else {
                throw error(res.status, 'User not found');
            }
        } catch (e) {
            console.error('Error fetching user profile:', e);
            throw error(500, `User ${username} not found`);
        }
    }
    }