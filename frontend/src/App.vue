<script setup>
import { ref } from "vue";
import axios from "axios";
import TopBar from "./components/TopBar.vue";
import DropZone from "./components/DropZone.vue";
import HeaderZone from "./components/HeaderZone.vue";
import SubmitZone from "./components/SubmitZone.vue";

const file = ref(null);
const to_email = ref(null);
const transcriptionStatus = ref("Waiting. Patiently. Mostly.");

function handleFileSelected(recievedFile) {
    file.value = recievedFile;
    console.log("File:", file.value);
}

async function sendFile() {
    if (!file.value) {
        console.error("No file selected");
        return;
    }

    const formData = new FormData();
    formData.append("audio_file", file.value);
    formData.append("email", to_email.value);

    console.log("Sending file:", file.value.name);
    console.log("Sending email:", to_email.value);
    console.log("FormData entries:", Array.from(formData.entries()));

    try {
        const apiUrl = import.meta.env.VITE_API_URL;
        const response = await axios.post(`${apiUrl}/transcribe`, formData);
        transcriptionStatus.value =
            "Heads up: this status bar is decorative. The real answer lands in ur inbox.";
        console.log("Success:", response.data);
    } catch (error) {
        console.error("Error:", error);
        console.error("Response data:", error.response?.data);
        console.error("Detail:", error.response?.data?.detail);
        console.error("Response status:", error.response?.status);
        transcriptionStatus.value = "Failed. Check console for details.";
    }
}
</script>

<template>
    <div id="app">
        <div class="container">
            <!-- <TopBar /> -->
            <p class="title">whisper<span>●</span>api</p>
            <div class="wrapper">
                <HeaderZone />
                <DropZone @file-selected="handleFileSelected" />
                <SubmitZone
                    v-model:email="to_email"
                    :can-send="!!file"
                    :status="transcriptionStatus"
                    @send="sendFile"
                />
            </div>
            <footer>
                <p>
                    <span>●</span> Powered by a Raspberry Pi and sheer
                    stubbornness
                </p>
            </footer>
        </div>
    </div>
</template>

<style scoped>
#app {
    background-color: var(--color-bg);
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: "Anthropic Sans";
}
.container {
    max-width: 800px;
    width: 800px;
    height: 100vh;
    margin: 0 auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.title {
    color: #141413;
    font-weight: bold;
}
.wrapper {
    display: flex;
    fjustify-content: center;
    align-items: center;
    flex-direction: column;
    gap: 20px;
}
footer {
    text-align: center;
    color: #141413;
    /*font-family: "The Girl Next Door", cursive;*/
}
</style>
