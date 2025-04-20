import { Box } from "@mui/material"; // MUI 컴포넌트 사용

// 필요한 컴포넌트들 (나중에 생성)
// import Sidebar from '../components/Sidebar';
// import ChatWindow from '../components/ChatWindow';

const ChatPage: React.FC = () => {
  return (
    <Box sx={{ display: "flex", width: "100%", height: "100%" }}>
      {/* 임시 사이드바 영역 */}
      <Box
        sx={{ width: "260px", borderRight: "1px solid #dee2e6", p: 2, backgroundColor: "#f8f9fa" }}
      >
        Sidebar Placeholder
      </Box>
      {/* 임시 채팅 영역 */}
      <Box sx={{ flexGrow: 1, p: 2, display: "flex", flexDirection: "column" }}>
        Chat Window Placeholder
      </Box>
    </Box>
  );
};

export default ChatPage;
