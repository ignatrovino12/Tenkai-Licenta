<script lang="ts">
    import { onMount } from "svelte";
    import {
        get_cookie_values,
        is_logged,
        SERVER_URL,
        redirectToHome,
        redirectToLogin,
        redirectToSignUp,
        redirectToProfile,
        redirectToUpload,
        logout_user,
        wait,
    } from "../../lib/utils";

    let username: string;
    let csrfToken: string;
    let video_signedUrl: string;
    let gpx_signedUrl: string;
    let selectedVideoName: string;
    let selectedGPXName: string;
    let selectedFileName: string;
    let videoName: string;
    let description='';
    let description2='';

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
                    description: description,
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

    async function generateSignedUrl_video_gpx(videoName: string) {
        try {
            const response = await fetch(`${SERVER_URL}/upload_video_gpx/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    username: username,
                    csrf_token: csrfToken,
                    video_name: videoName,
                    description: description2,
                }),
            });
            const data = await response.json();
            if (response.ok) {
                video_signedUrl = data.video_url;
                gpx_signedUrl = data.gpx_url;
            } else {
                console.error("Failed to generate signed URL.");
            }
        } catch (error) {
            console.error("Error:", error);
        }
    }

    async function handleGPXUpload(mp4File: string) {
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

        if (description.length > 200) {
            alert('Description must be less than 200 characters.');
            return;
        }

        try {
            await generateSignedUrl_video(selectedFileName);
            if (video_signedUrl) {
                const fileInput = document.querySelector(
                    'input[type="file"]',
                ) as HTMLInputElement;
                if (fileInput) {
                    const file = fileInput.files ? fileInput.files[0] : null;
                    if (file) {
                        // video upload

                        const response = await fetch(video_signedUrl, {
                            method: "PUT",
                            body: file,
                        });

                        if (response.ok) {
                            console.log("Video uploaded successfully.");

                            //gpx transformation and upload
                            const gpxUploadSuccess = await handleGPXUpload(
                                file.name,
                            );
                            if (gpxUploadSuccess) {
                                // update city/country

                                let requestData = {
                                    username: username,
                                    csrf_token: csrfToken,
                                    video_name: file.name,
                                };

                                let responseCityCountry = await fetch(
                                    `${SERVER_URL}/update_city_country/`,
                                    {
                                        method: "POST",
                                        headers: {
                                            "Content-Type": "application/json",
                                        },
                                        body: JSON.stringify(requestData),
                                    },
                                );

                                if (responseCityCountry.ok) {
                                    alert("Video uploaded successfully.");
                                } else {
                                    alert(
                                        "Video uploaded successfully but it does not contain any GPS metadata.",
                                    );
                                }
                            }
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

    async function handleFileUpload2(event: Event) {

        if (description2.length > 200) {
            alert('Description must be less than 200 characters.');
            return;
        }

        try {
            await generateSignedUrl_video_gpx(selectedVideoName);
            if (video_signedUrl) {
                const videoFileInput = document.getElementById(
                    "videoFile",
                ) as HTMLInputElement;
                const videoFile = videoFileInput.files
                    ? videoFileInput.files[0]
                    : null;

                if (videoFile) {
                    videoName = videoFile.name;
                    const videoResponse = await fetch(video_signedUrl, {
                        method: "PUT",
                        headers: {
                            "Content-Type": "video/mp4",
                        },
                        body: videoFile,
                    });

                    if (videoResponse.ok) {
                        console.log("Video uploaded successfully.");
                    } else {
                        console.error("Failed to upload video.");
                    }
                } else {
                    console.error("No video file selected.");
                }
            }

            // Upload GPX
            if (gpx_signedUrl) {
                const gpxFileInput = document.getElementById(
                    "gpxFile",
                ) as HTMLInputElement;
                const gpxFile = gpxFileInput.files
                    ? gpxFileInput.files[0]
                    : null;

                if (gpxFile) {
                    const gpxResponse = await fetch(gpx_signedUrl, {
                        method: "PUT",
                        headers: {
                            "Content-Type": "application/gpx+xml",
                        },
                        body: gpxFile,
                    });

                    if (gpxResponse.ok) {
                        console.log("GPX uploaded successfully.");

                        // update city/country

                        let requestData = {
                            username: username,
                            csrf_token: csrfToken,
                            video_name: videoName,
                        };

                        let responseCityCountry = await fetch(
                            `${SERVER_URL}/update_city_country/`,
                            {
                                method: "POST",
                                headers: {
                                    "Content-Type": "application/json",
                                },
                                body: JSON.stringify(requestData),
                            },
                        );

                        if (responseCityCountry.ok) {
                            alert("Video uploaded successfully.");
                        } else {
                            alert(
                                "Video uploaded successfully but it does not contain any GPS metadata.",
                            );
                        }
                    } else {
                        console.error("Failed to upload GPX.");
                    }
                } else {
                    console.error("No GPX file selected.");
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

    function handleVideoFileChange(event: Event) {
        const fileInput = event.target as HTMLInputElement;
        if (fileInput.files && fileInput.files.length > 0) {
            selectedVideoName = fileInput.files[0].name;
        }
    }

    function handleGpxFileChange(event: Event) {
        const fileInput = event.target as HTMLInputElement;
        if (fileInput.files && fileInput.files.length > 0) {
            selectedGPXName = fileInput.files[0].name;
        }
    }
</script>

<!-- Taskbar -->
<button on:click={logout_user}>Logout</button>
<button on:click={redirectToHome}>Home</button>
<button on:click={redirectToProfile}>Profile</button>
<button on:click={redirectToUpload}>Upload</button>
<button on:click={redirectToLogin}>Login</button>
<button on:click={redirectToSignUp}>Sign up</button>

<h1>Upload MP4 File</h1>

<form on:submit|preventDefault={handleFileUpload}>
    <label for="File">MP4 Video:</label>
    <input type="file" accept=".mp4" on:change={handleFileChange} />
    <label for="description">Description (a few words):</label>
    <textarea id="description" bind:value={description} rows="4" cols="50"></textarea>
    <button type="submit" disabled={!selectedFileName}>Upload</button>
</form>

<h1>Upload MP4 File and GPX File</h1>
<form on:submit|preventDefault={handleFileUpload2}>
    <div>
        <label for="videoFile">MP4 Video:</label>
        <input
            type="file"
            id="videoFile"
            accept=".mp4"
            on:change={handleVideoFileChange}
        />
    </div>
    <div>
        <label for="gpxFile">GPX File:</label>
        <input
            type="file"
            id="gpxFile"
            accept=".gpx"
            on:change={handleGpxFileChange}
        />
    </div>
    <label for="description2">Description (a few words):</label>
    <textarea id="description2" bind:value={description2} rows="4" cols="50"></textarea>
    <p></p>
    <button type="submit" disabled={!selectedVideoName || !selectedGPXName}
        >Upload</button
    >
    
</form>

<style>
    textarea {
        resize: none; 
    }
</style>
