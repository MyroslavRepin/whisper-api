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
const statusType = ref("idle"); // idle | loading | success | error
const sending = ref(false);

function handleFileSelected(recievedFile) {
    file.value = recievedFile;
    console.log("File:", file.value);
}

function setStatus(type, message) {
    statusType.value = type;
    transcriptionStatus.value = message;
}

async function sendFile() {
    if (!file.value) {
        setStatus("error", "Pick a file first. I can't transcribe vibes.");
        return;
    }
    if (!to_email.value) {
        setStatus("error", "No email, no transcript. Where do I send it?");
        return;
    }

    const formData = new FormData();
    formData.append("audio_file", file.value);
    formData.append("email", to_email.value);

    sending.value = true;
    setStatus("loading", "Uploading… the Pi is limbering up.");

    try {
        const apiUrl = import.meta.env.VITE_API_URL;
        const response = await axios.post(`${apiUrl}/transcribe`, formData);
        setStatus(
            "success",
            "Got it! Transcribing in the background — the result lands in ur inbox.",
        );
        console.log("Success:", response.data);
    } catch (error) {
        console.error("Error:", error, error.response?.data);

        let errorMsg = "Something broke. Unknown error.";
        const detail = error.response?.data?.detail;
        if (Array.isArray(detail)) {
            errorMsg = detail
                .map((e) => `${e.loc?.join(".")}: ${e.msg}`)
                .join(", ");
        } else if (typeof detail === "string") {
            errorMsg = detail;
        } else if (!error.response) {
            errorMsg = "Can't reach the server. The Pi might be napping.";
        } else {
            errorMsg = `Server said ${error.response.status}. It wasn't a compliment.`;
        }
        setStatus("error", errorMsg);
    } finally {
        sending.value = false;
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
                    :sending="sending"
                    :status="transcriptionStatus"
                    :status-type="statusType"
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
