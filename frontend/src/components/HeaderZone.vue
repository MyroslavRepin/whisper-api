<template>
    <section class="steps">
        <ol>
            <li>Select an audio file.</li>
            <li>Enter your email address.</li>
            <li>Receive the transcript when processing finishes.</li>
        </ol>
    </section>
</template>

<style scoped>
.steps {
    color: var(--color-muted);
    font-size: 14px;
}
ol {
    list-style: none;
    counter-reset: step;
    display: flex;
    flex-direction: column;
    gap: 4px;
}
li {
    counter-increment: step;
    display: flex;
    gap: 10px;
}
li::before {
    content: counter(step);
    font-variant-numeric: tabular-nums;
    color: var(--color-fg);
    font-weight: 600;
    min-width: 1ch;
}
</style>
