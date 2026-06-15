/**
 * @file Vite build configuration file.
 * Defines global plugins and compilation settings for the Vue 3 frontend application.
 */
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  /**
   * @property {Array} plugins - List of enabled Vite plugins.
   * Includes the official Vue plugin to enable compilation of Single File Components (.vue).
   */
  plugins: [vue()],
})
