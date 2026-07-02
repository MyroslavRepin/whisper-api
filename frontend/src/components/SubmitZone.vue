<script setup>
const email = defineModel("email");
defineProps({
    canSend: Boolean,
    sending: Boolean,
    status: String,
    statusType: String,
});
const emit = defineEmits(["send"]);
</script>

<template>
    <main>
        <div class="wrapper">
            <div class="input-row">
                <input
                    v-model="email"
                    type="email"
                    placeholder="Where do I dump the results?"
                    :disabled="sending"
                />
                <button
                    v-if="canSend"
                    :disabled="sending"
                    @click="emit('send')"
                >
                    <span v-if="sending" class="spinner"></span>
                    {{ sending ? "Sending…" : "Send file" }}
                </button>
            </div>
            <p>
                Transcription status:
                <span class="status" :class="statusType">
                    <span v-if="statusType === 'error'">✗ </span>
                    <span v-else-if="statusType === 'success'">✓ </span>
                    {{ status }}
                </span>
            </p>
        </div>
    </main>
</template>

<style scoped>
main {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    padding: 20px;
    background-color: var(--color-secondary);
    border-radius: 8px;
    width: 100%;
}
.wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 15px;
    width: 100%;
}
.input-row {
    display: flex;
    flex-direction: row;
    gap: 12px;
    width: 100%;
    max-width: 400px;
    align-items: stretch;
}
input {
    padding: 12px 16px;
    border-radius: 8px;
    border: 2px solid #e0e0e0;
    flex: 1;
    font-family: "The Girl Next Door", cursive;
    font-size: 18px;
    font-weight: 600;
    transition: border-color 0.2s ease;
}
input:focus {
    outline: none;
    border-color: var(--color-span);
}
input:disabled {
    opacity: 0.6;
}
button {
    padding: 12px 24px;
    border-radius: 8px;
    border: none;
    background-color: var(--color-span);
    color: white;
    font-family: "The Girl Next Door", cursive;
    font-size: 18px;
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}
button:disabled {
    opacity: 0.7;
    cursor: wait;
}
.spinner {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.4);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
}
@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

p {
    font-family: "Caveat", cursive;
    font-size: 22px;
}
.status.loading {
    color: #8a6d00;
    animation: pulse 1.2s ease-in-out infinite;
}
.status.success {
    color: #2e7d32;
}
.status.error {
    color: #c0392b;
}
@keyframes pulse {
    50% {
        opacity: 0.5;
    }
}
</style>
