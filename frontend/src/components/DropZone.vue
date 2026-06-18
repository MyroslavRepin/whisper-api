<script setup>
import { ref, onMounted } from "vue";
import rough from "roughjs";

const emit = defineEmits(["file-selected"]);
const file = ref(null);
const svg = ref(null);

const WIDTH = 400;
const HEIGHT = 200;
const SVG_NS = "http://www.w3.org/2000/svg";

function onFileChange(event) {
    const selected = event.target.files[0];
    if (!selected) return;
    file.value = selected;
    emit("file-selected", selected);
}

function draw() {
    const el = svg.value;
    if (!el) return;

    const rc = rough.svg(el);

    const rect = rc.rectangle(10, 10, WIDTH - 20, HEIGHT - 20, {
        roughness: 3,
        stroke: "#000",
        strokeWidth: 2,
        fill: "#cccccc",
        fillStyle: "hachure",
        hachureGap: 8,
        hachureAngle: -41,
        fillWeight: 1,
    });
    el.appendChild(rect);

    const text = document.createElementNS(SVG_NS, "text");
    text.setAttribute("x", WIDTH / 2);
    text.setAttribute("y", HEIGHT / 2);
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("dominant-baseline", "middle");
    text.setAttribute("fill", "#f25c54");
    text.style.fontFamily = '"Anthropic Sans"';
    text.style.fontSize = "44px";
    text.style.fontWeight = "700";
    text.textContent = "Drop ur audio";
    el.appendChild(text);
}

onMounted(() => {
    draw();
});
</script>

<template>
    <div class="drop-zone">
        <svg
            ref="svg"
            :viewBox="`0 0 ${WIDTH} ${HEIGHT}`"
            :width="WIDTH"
            :height="HEIGHT"
        ></svg>
        <input type="file" accept="audio/*" @change="onFileChange" />
        <p>File name: {{ file?.name || "No file selected" }}</p>
    </div>
</template>

<style scoped>
.drop-zone {
    display: flex;
    justify-content: center;
    flex-direction: column;
    align-items: center;
    position: relative;
}

svg {
    display: block;
}

input[type="file"] {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    opacity: 0;
    cursor: pointer;
}
p {
    font-family: "Caveat", cursive;
    font-size: 20px;
}
</style>
