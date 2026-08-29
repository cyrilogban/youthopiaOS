/// <reference types="vite/client" />

// Base URL of the YouThopiaOS gateway. Absent in dev (api.ts falls back to
// http://localhost:8000); set at build time in Module 5 for the deployed origin.
interface ImportMetaEnv {
  readonly VITE_GATEWAY_URL?: string;
}
