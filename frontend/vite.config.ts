import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // Docker 컨테이너 외부에서 접근 허용
    port: 5173, // Vite 기본 포트
    proxy: {
      // 프록시 설정
      // /api로 시작하는 요청을 백엔드(http://backend:8000)로 전달
      "/api": {
        target: "http://backend:8000", // Docker Compose 서비스 이름 사용
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""), // 요청 경로에서 /api 제거
      },
    },
  },
});
