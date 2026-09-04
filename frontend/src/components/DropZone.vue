<script setup>
import { ref } from "vue";

const emit = defineEmits(["file-selected"]);
const file = ref(null);
const input = ref(null);
const dragging = ref(false);

function select(selected) {
    if (!selected) return;
    file.value = selected;
    emit("file-selected", selected);
}

function onFileChange(event) {
    select(event.target.files[0]);
}

function onDrop(event) {
    dragging.value = false;
    select(event.dataTransfer?.files?.[0]);
}

function formatSize(bytes) {
    const mb = bytes / (1024 * 1024);
    return mb >= 1 ? `${mb.toFixed(1)} MB` : `${Math.max(1, Math.round(bytes / 1024))} KB`;
}
</script>

<template>
    <section>
        <div
            class="drop"
            :class="{ dragging, filled: !!file }"
            @click="input.click()"
            @dragover.prevent="dragging = true"
            @dragleave="dragging = false"
            @drop.prevent="onDrop"
        >
            <p class="label">Drop an audio file here, or click to browse</p>
            <p class="hint">mp3, m4a, wav, ogg — up to 3 hours</p>
            <input
                ref="input"
                type="file"
                accept="audio/*"
                @change="onFileChange"
            />
        </div>
        <p class="selected">
            <template v-if="file">
                <span class="name">{{ file.name }}</span>
                <span class="size">{{ formatSize(file.size) }}</span>
            </template>
            <template v-else>No file selected</template>
        </p>
    </section>
</template>

<style scoped>
.drop {
    border: 1px dashed var(--color-line);
    border-radius: var(--radius);
    background: var(--color-surface);
    padding: 40px 24px;
    text-align: center;
    cursor: pointer;
    transition:
        border-color 0.15s ease,
        background-color 0.15s ease;
}
.drop:hover,
.drop.dragging {
    border-color: var(--color-accent);
}
.drop.filled {
    border-style: solid;
}
.label {
    font-size: 15px;
}
.hint {
    margin-top: 4px;
    color: var(--color-muted);
    font-size: 13px;
}
input[type="file"] {
    display: none;
}
.selected {
    margin-top: 10px;
    font-family: var(--font-mono);
    font-size: 13px;
    color: var(--color-muted);
    display: flex;
    gap: 10px;
    justify-content: space-between;
}
.name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
</style>
