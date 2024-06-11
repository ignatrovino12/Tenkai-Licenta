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
        fetchProfilePicture,
    } from "../../lib/utils";
    import "../../app.css";

    let username: string;
    let csrfToken: string;
    let video_signedUrl: string;
    let gpx_signedUrl: string;
    let selectedVideoName: string;
    let selectedGPXName: string;
    let selectedFileName: string;
    let videoName: string;
    let description = "";
    let description2 = "";
    let profilePicture = "";
    let uploading = false;
    let uploading2 = false;

    onMount(async () => {
        const { username: u, csrfToken: token } = get_cookie_values();
        const response = await is_logged(u, token);
        if (response) {
            username = u;
            csrfToken = token;
        }

        const isBrowser = typeof window !== "undefined";

        if (isBrowser) {
            profilePicture = sessionStorage.getItem("profile_picture") || "";
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
                const message = data.message;
                console.error("Failed to generate signed URL.");
                alert(message);
                uploading = false;
            }
        } catch (error) {
            console.error("Error:", error);
            uploading = false;
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
                const message = data.message;
                console.error("Failed to generate signed URL.");
                alert(message);
                uploading2 = false;
            }
        } catch (error) {
            console.error("Error:", error);
            uploading2 = false;
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
            alert("Description must be less than 200 characters.");
            return;
        }

        try {
            uploading = true;
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

        uploading = false;
    }

    async function handleFileUpload2(event: Event) {
        if (description2.length > 200) {
            alert("Description must be less than 200 characters.");
            return;
        }

        try {
            uploading2 = true;
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
        uploading2 = false;
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

<svelte:head>
    <link
    rel="stylesheet"
    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
/>

    <title>Upload</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
</svelte:head>

<!-- Taskbar -->

<div
    class="h-screen w-48 bg-gray-800 fixed top-0 left-0 flex flex-col items-center py-4 shadow-lg"
>
    <div class="flex flex-col items-center mt-4">
        <div class="mb-8">
            {#if profilePicture}
                <img
                    src={profilePicture}
                    alt=""
                    class="w-16 h-16 rounded-full border-2 border-white"
                />
            {:else}
                <div
                    class="w-16 h-16 rounded-full border-2 border-white flex"
                ></div>
            {/if}
        </div>
        <button
            class="mb-4 w-full text-white py-2 px-4 rounded hover:bg-gray-700 flex items-center"
            on:click={logout_user}
        >
            <i class="fas fa-sign-out-alt mr-2"></i>Logout
        </button>
        <button
            class="mb-4 w-full text-white py-2 px-4 rounded hover:bg-gray-700 flex items-center"
            on:click={redirectToHome}
        >
            <i class="fas fa-home mr-2"></i>Home
        </button>
        <button
            class="mb-4 w-full text-white py-2 px-4 rounded hover:bg-gray-700 flex items-center"
            on:click={redirectToProfile}
        >
            <i class="fas fa-user mr-2"></i>Profile
        </button>
        <button
            class="mb-4 w-full text-white py-2 px-4 rounded hover:bg-gray-700 flex items-center"
            on:click={redirectToUpload}
        >
            <i class="fas fa-upload mr-2"></i>Upload
        </button>
        <button
            class="mb-4 w-full text-white py-2 px-4 rounded hover:bg-gray-700 flex items-center"
            on:click={redirectToLogin}
        >
            <i class="fas fa-sign-in-alt mr-2"></i>Login
        </button>
        <button
            class="mb-4 w-full text-white py-2 px-4 rounded hover:bg-gray-700 flex items-center"
            on:click={redirectToSignUp}
        >
            <i class="fas fa-user-plus mr-2"></i>Sign up
        </button>
    </div>
</div>


<!-- Uploads -->
<div class="flex justify-center mt-12 w-5/6 px-16 ml-52">
    <!-- First Upload Form -->
    <div class="w-1/3 h-120 p-8 bg-gray-100 rounded-lg mr-12">
        <h1 class="text-lg font-bold mb-4">Upload MP4 File</h1>
        <form on:submit|preventDefault={handleFileUpload}>
            <label for="File" class="block mb-2">MP4 Video and Name:</label>
            <input
                type="file"
                accept=".mp4"
                on:change={handleFileChange}
                class="mb-4"
            />

            <label for="description" class="block mb-2"
                >Description (a few words):</label
            >
            <div class="flex mb-4">
                <textarea
                    id="description"
                    bind:value={description}
                    rows="6"
                    class="flex-1 mr-4"
                ></textarea>
            </div>
            <button
                type="submit"
                disabled={!selectedFileName || uploading2}
                class=" w-full bg-blue-500 text-white py-2 px-4 rounded disabled:bg-gray-400 disabled:cursor-not-allowed"
                >Upload</button
            >
        </form>
        {#if uploading}
            <p class="text-center mt-2 uploading-animation"></p>
        {/if}
    </div>

    <!-- Second Upload Form -->
    <div class="w-1/3 h-120 p-8 bg-gray-100 rounded-lg mr-8">
        <h1 class="text-lg font-bold mb-4">Upload MP4 File and GPX File</h1>
        <form on:submit|preventDefault={handleFileUpload2}>
            <div class="mb-4">
                <label for="videoFile" class="block mb-2"
                    >MP4 Video and Name:</label
                >
                <input
                    type="file"
                    id="videoFile"
                    accept=".mp4"
                    on:change={handleVideoFileChange}
                    class="mb-2"
                />
            </div>
            <div class="mb-4">
                <label for="gpxFile" class="block mb-2">GPX File:</label>
                <input
                    type="file"
                    id="gpxFile"
                    accept=".gpx"
                    on:change={handleGpxFileChange}
                    class="mb-2"
                />
            </div>
            <label for="description2" class="block mb-2"
                >Description (a few words):</label
            >
            <div class="flex mb-4">
                <textarea
                    id="description2"
                    bind:value={description2}
                    rows="6"
                    class="flex-1 mr-4"
                ></textarea>
            </div>
            <button
                type="submit"
                disabled={!selectedVideoName || !selectedGPXName || uploading}
                class="w-full bg-blue-500 text-white py-2 px-4 rounded disabled:bg-gray-400 disabled:cursor-not-allowed"
                >Upload</button
            >
        </form>
        {#if uploading2}
            <p class="text-center mt-2 uploading-animation"></p>
        {/if}
    </div>
</div>

<!-- Disclaimer -->

<div class="mt-8 ml-52 flex justify-center">
    <div class="w-1/2 bg-gray-100 rounded-lg p-4">
        <p class="text-center">
            Please wait for the video to finish uploading (it may take some
            time).
        </p>
        <p class="text-center">
            Also, ensure that all the videos you upload have different names.
        </p>
    </div>
</div>
