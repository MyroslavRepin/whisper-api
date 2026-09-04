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
    <section>
        <form class="row" @submit.prevent="emit('send')">
            <label class="field">
                <span class="field-label">Send transcript to</span>
                <input
                    v-model="email"
                    type="email"
                    autocomplete="email"
                    placeholder="you@example.com"
                    :disabled="sending"
                />
            </label>
            <button type="submit" :disabled="sending || !canSend">
                {{ sending ? "Uploading…" : "Transcribe" }}
            </button>
        </form>

        <p class="status" :class="statusType">
            <span class="status-label">Status</span>
            <span>{{ status }}</span>
        </p>
    </section>
</template>

<style scoped>
.row {
    display: flex;
    align-items: flex-end;
    gap: 10px;
}
.field {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.field-label {
    font-size: 13px;
    color: var(--color-muted);
}
input {
    padding: 10px 12px;
    border: 1px solid var(--color-line);
    border-radius: var(--radius);
    background: var(--color-surface);
    font-size: 15px;
    width: 100%;
}
input:focus {
    outline: none;
    border-color: var(--color-accent);
}
input:disabled {
    opacity: 0.6;
}
button {
    padding: 10px 18px;
    border: 1px solid var(--color-fg);
    border-radius: var(--radius);
    background: var(--color-fg);
    color: var(--color-bg);
    font-size: 15px;
    cursor: pointer;
    white-space: nowrap;
}
button:disabled {
    background: transparent;
    color: var(--color-muted);
    border-color: var(--color-line);
    cursor: not-allowed;
}
.status {
    margin-top: 14px;
    padding-top: 12px;
    border-top: 1px solid var(--color-line);
    display: flex;
    gap: 12px;
    font-family: var(--font-mono);
    font-size: 13px;
    color: var(--color-muted);
}
.status-label {
    color: var(--color-muted);
    min-width: 6ch;
}
.status.loading span:last-child::after {
    content: "";
    animation: dots 1.2s steps(4, end) infinite;
}
.status.success span:last-child {
    color: var(--color-ok);
}
.status.error span:last-child {
    color: var(--color-accent);
}
@keyframes dots {
    0% { content: ""; }
    25% { content: "."; }
    50% { content: ".."; }
    75% { content: "..."; }
}
@media (max-width: 520px) {
    .row {
        flex-direction: column;
        align-items: stretch;
    }
}
</style>
