<script lang="ts">
    import { onMount } from "svelte";
    import { get_cookie_values, is_logged, SERVER_URL } from "../../lib/utils";

    let username: string;
    let csrfToken: string;
    let video_signedUrl: string;
    let gpx_signedUrl: string;
    let selectedFileName: string;

    onMount(async () => {
        const { username: u, csrfToken: token } = get_cookie_values();
        const response = await is_logged(u, token);
        if (response) {
            username = u;
            csrfToken = token;
        }
    });

    async function generateSignedUrl_video(videoName: string) {
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
                video_signedUrl = data.signed_url;
            } else {
                console.error("Failed to generate signed URL.");
            }
        } catch (error) {
            console.error("Error:", error);
        }
    }

    async function handleGPXUpload(mp4File: File) {
        try {
            let formData = new FormData();
            formData.append("mp4_file", mp4File);
            formData.append("username", username);
            formData.append("csrf_token", csrfToken);

            let response = await fetch(`${SERVER_URL}/convert_gpx/`, {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                let result = await response.json();
                if (result.success) {
                    console.log(result.message);
                    return true;
                } else {
                    console.error("Error:", result.message);
                    return false;
                }
            } else {
                console.error("Error:", response.statusText);
                return false;
            }
        } catch (error) {
            console.error("Error:", error);
            return false;
        }
    }

    async function handleFileUpload(event: Event) {
        event.preventDefault();
        try {
            await generateSignedUrl_video(selectedFileName);
            if (video_signedUrl) {
                const fileInput = document.querySelector(
                    'input[type="file"]',
                ) as HTMLInputElement;
                if (fileInput) {
                    const file = fileInput.files ? fileInput.files[0] : null;
                    if (file) {
                        // gpx transformation and upload
                        const gpxUploadSuccess = await handleGPXUpload(file);
                        
                        if (gpxUploadSuccess) {
      
                            const response = await fetch(video_signedUrl, {
                                method: "PUT",
                                body: file,
                            });
                            if (response.ok) {
                                console.log("File uploaded successfully.");
                            } else {
                                console.error("Failed to upload file.");
                            }
                        } else {
                            console.error("GPX upload failed.");
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
