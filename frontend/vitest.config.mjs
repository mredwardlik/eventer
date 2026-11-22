import path from "node:path";
import { defineConfig } from "vitest/config";

export default defineConfig({
    resolve: {
        alias: {
            src: path.resolve(__dirname, "src"),
            styles: path.resolve(__dirname, "src/assets/styles"),
        },
    },
    esbuild: { jsx: "automatic" },
    test: {
        environment: "jsdom",
        setupFiles: ["./src/__tests__/setup.ts"],
        css: false, // styles do not matter for these tests
    },
});
