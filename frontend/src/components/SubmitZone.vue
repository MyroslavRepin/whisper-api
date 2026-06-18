<script setup>
const email = defineModel("email");
defineProps({
    canSend: Boolean,
    status: String,
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
                />
                <button v-if="canSend" @click="emit('send')">Send file</button>
            </div>
            <p>
                Transcription status: <span>{{ status }}</span>
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
}

p {
    font-family: "Caveat", cursive;
    font-size: 22px;
}
</style>
