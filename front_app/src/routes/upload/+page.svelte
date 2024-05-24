<script lang="ts">
    import { onMount } from "svelte";
    import { get_cookie_values, is_logged, SERVER_URL } from "../../lib/utils";
    // import { exec } from 'node:child_process';


    let username: string;
    let csrfToken: string;
    let video_signedUrl: string;
    let gpx_signedUrl : string;
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

    async function generateSignedUrl_gpx(gpxName: string) {
        try {
            const response = await fetch(`${SERVER_URL}/upload_gpx/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    username: username,
                    csrf_token: csrfToken,
                    gpx_name: gpxName,
                }),
            });
            const data = await response.json();
            if (response.ok) {
                gpx_signedUrl = data.signed_url;
                return gpx_signedUrl
            } else {
                console.error("Failed to generate signed URL.");
            }
        } catch (error) {
            console.error("Error:", error);
        }
    }

    // async function handleGpxTransformation(file: File) {
    //     const exifToolPath = "../../lib/exiftool.exe";
    //     const gpxFmtPath = "../../lib/gpx.fmt";

    //     exec(
    //         `"${exifToolPath}" -p "${gpxFmtPath}" -ee -`,
    //         async (error: Error | null, stdout : string, stderr: string) => {
    //             if (error) {
    //                 console.error(`Error executing command: ${error}`);
    //                 return;
    //             }

    //             const gpxSignedUrl = await generateSignedUrl_gpx(`${file.name}.gpx`);

    //             if (gpxSignedUrl) {
    //                 const gpxResponse = await fetch(gpxSignedUrl, {
    //                     method: "PUT",
    //                     body : stdout,
    //                 });
    //                 if (gpxResponse.ok) {
    //                     console.log(".gpx file uploaded successfully.");
    //                 } else {
    //                     console.error("Failed to upload .gpx file.");
    //                 }
    //             }
    //         },
    //     ).stdin!.write(file);;
    // }

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
                        const response = await fetch(video_signedUrl, {
                            method: "PUT",
                            body: file,
                        });
                        if (response.ok) {
                            console.log("File uploaded successfully.");
                            
                            // gpx
                            // await handleGpxTransformation(file);
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
