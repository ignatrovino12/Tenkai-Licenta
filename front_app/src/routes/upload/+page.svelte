<script lang="ts">
    import { onMount } from "svelte";
    import { get_cookie_values, is_logged, SERVER_URL } from "../../lib/utils";

    let username: string;
    let csrfToken: string;
    let signedUrl: string;
    let selectedFileName: string;
    let user_id = 0;

    onMount(async () => {
        const { username: u, csrfToken: token } = get_cookie_values();
        const response = await is_logged(u, token);
        if (response) {
            username = u;
            csrfToken = token;
        }
    });

    async function generateSignedUrl(videoName: string) {
        try {
            const response = await fetch(`${SERVER_URL}/upload_video/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    username: username,
                    csrf_token: csrfToken,
                    video_name: videoName,
                }),
            });
            const data = await response.json();
            if (response.ok) {
                signedUrl = data.signed_url;
                user_id = data.user_id;
            } else {
                console.error("Failed to generate signed URL.");
            }
        } catch (error) {
            console.error("Error:", error);
        }
    }

    async function handleFileUpload(event: Event) {
        event.preventDefault();
        try {
            await generateSignedUrl(selectedFileName); // Pass the selected file name
            if (signedUrl) {
                const formData = new FormData();
                formData.append("username", username);
                formData.append("user_id", user_id.toString()); 

                const fileInput = document.querySelector(
                    'input[type="file"]',
                ) as HTMLInputElement;
                if (fileInput) {
                    const file = fileInput.files ? fileInput.files[0] : null;
                    if (file) {
                        formData.append("mp4_video", file);

                        const response = await fetch(signedUrl, {
                            method: "PUT",
                            body: formData,
                        });
                        if (response.ok) {
                            console.log("File uploaded successfully.");
                        } else {
                            console.error("Failed to upload file.");
                        }
                    } else {
                        console.error("No file selected.");
                    }
                } else {
                    console.error("File input not found.");
                }
            }
        } catch (error) {
            console.error("Error:", error);
        }
    }

    function handleFileChange(event: Event) {
        const fileInput = event.target as HTMLInputElement;
        if (fileInput.files && fileInput.files.length > 0) {
            selectedFileName = fileInput.files[0].name;
        }
    }
</script>

<h1>Upload MP4 File</h1>

<form on:submit|preventDefault={handleFileUpload}>
    <input type="file" accept=".mp4" on:change={handleFileChange} />
    <button type="submit">Upload</button>
</form>
