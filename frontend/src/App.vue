<script setup>
import { ref } from "vue";
import axios from "axios";
import DropZone from "./components/DropZone.vue";
import HeaderZone from "./components/HeaderZone.vue";
import SubmitZone from "./components/SubmitZone.vue";

const file = ref(null);
const to_email = ref(null);
const transcriptionStatus = ref("Idle — no file submitted yet.");
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

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function readErrorMessage(error) {
    if (!error.response) {
        return error.code === "ECONNABORTED"
            ? "Upload timed out. Try a smaller file."
            : "Cannot reach the server. Check your connection and retry.";
    }

    const detail = error.response.data?.detail;
    if (typeof detail === "string") return detail;
    // Older/raw FastAPI validation payload: list of {loc, msg}.
    if (Array.isArray(detail) && detail.length) {
        return detail
            .map((e) => `${e.loc?.slice(-1)[0] ?? "field"}: ${e.msg}`)
            .join(", ");
    }
    if (error.response.status === 413) return "That file is too large to upload.";
    return `Request failed (HTTP ${error.response.status}). Please retry.`;
}

async function sendFile() {
    if (!file.value) {
        setStatus("error", "Select an audio file first.");
        return;
    }

    const email = (to_email.value || "").trim();
    if (!email) {
        setStatus("error", "Enter the email address to send the transcript to.");
        return;
    }
    if (!EMAIL_RE.test(email)) {
        setStatus("error", `"${email}" is not a valid email address.`);
        return;
    }

    const formData = new FormData();
    formData.append("audio_file", file.value);
    formData.append("email", email);

    sending.value = true;
    setStatus("loading", "Uploading…");

    try {
        const apiUrl = import.meta.env.VITE_API_URL;
        const response = await axios.post(`${apiUrl}/transcribe`, formData, {
            timeout: 10 * 60 * 1000,
        });
        setStatus(
            "success",
            `Uploaded. Transcribing now — the transcript will arrive at ${email}.`,
        );
        console.log("Success:", response.data);
    } catch (error) {
        console.error("Error:", error, error.response?.data);
        setStatus("error", readErrorMessage(error));
    } finally {
        sending.value = false;
    }
}
</script>

<template>
    <div class="page">
        <header class="masthead">
            <h1 class="wordmark">whisper<span class="dot">.</span>api</h1>
            <p class="tagline">
                Audio in, plain-text transcript in your inbox. No account, no
                storage after delivery.
            </p>
        </header>

        <main class="main">
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
        </main>

        <footer class="footer">
            <p>Runs on a Raspberry Pi. Files are deleted after transcription.</p>
        </footer>
    </div>
</template>

<style scoped>
.page {
    max-width: 620px;
    margin: 0 auto;
    padding: 64px 24px 32px;
    display: flex;
    flex-direction: column;
    gap: 48px;
    min-height: 100vh;
}

.masthead {
    border-bottom: 1px solid var(--color-line);
    padding-bottom: 20px;
}

.wordmark {
    font-size: 20px;
    font-weight: 600;
    letter-spacing: -0.01em;
}

.dot {
    color: var(--color-accent);
}

.tagline {
    margin-top: 6px;
    color: var(--color-muted);
    font-size: 15px;
    max-width: 46ch;
}

.main {
    display: flex;
    flex-direction: column;
    gap: 28px;
    flex: 1;
}

.footer {
    border-top: 1px solid var(--color-line);
    padding-top: 16px;
    color: var(--color-muted);
    font-size: 13px;
}

@media (max-width: 600px) {
    .page {
        padding: 32px 20px 24px;
        gap: 32px;
    }
}
</style>
