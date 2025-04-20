// import React from "react"; // 삭제
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { CssBaseline, Box } from "@mui/material"; // MUI 컴포넌트 임포트

// 페이지 컴포넌트 임포트 (다음 단계에서 생성)
import ChatPage from "./pages/ChatPage";
import AdminPage from "./pages/AdminPage";

function App() {
  return (
    <Router>
      {/* CssBaseline: 브라우저 기본 스타일 초기화 및 MUI 테마 적용 */}
      <CssBaseline />
      {/* 전체 앱 레이아웃을 위한 Box 컴포넌트 (div 역할) */}
      <Box sx={{ display: "flex", height: "100%" }}>
        <Routes>
          {/* 루트 경로: ChatPage 렌더링 */}
          <Route path="/" element={<ChatPage />} />
          {/* /admin 경로: AdminPage 렌더링 */}
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </Box>
    </Router>
  );
}

export default App;
