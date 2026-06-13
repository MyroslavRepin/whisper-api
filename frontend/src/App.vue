<script setup>
import { ref } from "vue";
import axios from "axios";
import TopBar from "./components/TopBar.vue";
import DropZone from "./components/DropZone.vue";

const file = ref(null);
const transcriptionStatus = ref("No file selected");

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

    try {
        const response = await axios.post(
            "http://localhost:8080/api/v1/transcribe",
            formData,
            { headers: { "Content-Type": "multipart/form-data" } },
        );
        transcriptionStatus.value = "Transcription in progress...";
        console.log("Success:", response.data);
    } catch (error) {
        console.error("Error:", error);
    }
}
</script>

<template>
    <div id="app">
        <div class="container">
            <!-- <TopBar /> -->
            <DropZone @file-selected="handleFileSelected" />
            <button v-if="file" @click="sendFile">Send file</button>
            <p>Transcription status: {{ transcriptionStatus }}</p>
        </div>
    </div>
</template>

<style scoped>
#app {
    background-color: var(--color-bg);
    display: flex;
    justify-content: center;
}
.container {
    max-width: 800px;
    width: 800px;
    margin: 0 auto;
    padding: 20px;
}
</style>
