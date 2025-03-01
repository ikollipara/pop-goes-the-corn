/**------------------------------------------------------------
 * rollup.config.mjs
 * Ian Kollipara
 *
 * Rollup Configuration
 *------------------------------------------------------------**/

import { defineConfig } from "rollup";
import { nodeResolve } from "@rollup/plugin-node-resolve";

export default defineConfig({
  plugins: [nodeResolve()],
  input: "static/src/app.js",
  output: {
    dir: "static/dist",
  },
});
