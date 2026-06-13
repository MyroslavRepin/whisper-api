<script setup>
import { ref } from "vue";

const emit = defineEmits(["file-selected"]);
const file = ref(null);

function onFileChange(event) {
    file.value = event.target.files[0];
}

function onSubmit() {
    if (file.value) {
        emit("file-selected", file.value);
    }
}
</script>

<template>
    <div class="drop-zone">
        <input type="file" accept="audio/*" @change="onFileChange" />
        <button @click="onSubmit">Отправить</button>
    </div>
</template>
