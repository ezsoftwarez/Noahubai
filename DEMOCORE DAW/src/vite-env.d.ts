/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_OS_HOSTNAME: string;
  readonly VITE_OS_USER: string;
  readonly VITE_BRIDGE_URL: string;
  readonly VITE_NOAHUBAI_URL: string;
  readonly VITE_AIHUB_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
