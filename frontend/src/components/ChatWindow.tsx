import { useState, useRef, useEffect } from "react";
import {
  Box,
  TextField,
  List,
  ListItem,
  Paper,
  Typography,
  CircularProgress,
  IconButton,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// ChatPage에서 정의한 Message 타입 임포트
import { Message } from "../pages/ChatPage";
// API 서비스 임포트
import { sendMessage } from "../services/api";

interface ChatWindowProps {
  sessionId: string | null;
  messages: Message[];
  loadingHistory: boolean;
  addMessageToList: (message: Message) => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({
  sessionId,
  messages,
  loadingHistory,
  addMessageToList,
}) => {
  const [inputMessage, setInputMessage] = useState<string>("");
  const [sending, setSending] = useState<boolean>(false);
  const chatBoxRef = useRef<HTMLDivElement>(null); // 스크롤 제어를 위한 ref

  // 메시지 목록이 변경될 때마다 맨 아래로 스크롤
  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  // 메시지 전송 핸들러
  const handleSendMessage = async () => {
    const trimmedMessage = inputMessage.trim();
    if (!trimmedMessage || !sessionId || sending) return;

    setSending(true);
    setInputMessage("");

    // 1. 사용자 메시지를 즉시 UI에 추가
    const userMessage: Message = { role: "user", content: trimmedMessage };
    addMessageToList(userMessage);

    try {
      // 2. API 호출
      const response = await sendMessage(sessionId, trimmedMessage);

      // 3. 봇 응답을 UI에 추가
      if (response && response.response) {
        const botMessage: Message = { role: "bot", content: response.response };
        addMessageToList(botMessage);
      }
      // 4. 세션 목록 업데이트 (옵션 - 최신순 정렬 위해 ChatPage에서 처리)
      // await loadSessionList();
      // renderSessionList();
    } catch (error) {
      console.error("메시지 전송 오류:", error);
      addMessageToList({ role: "bot", content: "메시지 전송 중 오류가 발생했습니다." });
    } finally {
      setSending(false);
    }
  };

  // Enter 키로 메시지 전송
  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault(); // 기본 동작(줄바꿈) 방지
      handleSendMessage();
    }
  };

  return (
    <Box
      sx={{
        flexGrow: 1,
        display: "flex",
        flexDirection: "column",
        height: "100%",
        overflow: "hidden",
        backgroundColor: "white", // 채팅창 배경색
      }}
    >
      {/* 메시지 목록 영역 */}
      <Box
        ref={chatBoxRef}
        sx={{
          flexGrow: 1,
          overflowY: "auto",
          minHeight: 0,
          py: 3, // 상하 패딩 유지
          px: { xs: 4, sm: 6, md: 8, lg: 15, xl: 20 }, // 좌우 패딩 증가 (반응형)
          mb: 1,
          backgroundColor: "#f9f9f9",
        }}
      >
        {loadingHistory ? (
          <Box
            sx={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100%" }}
          >
            <CircularProgress />
          </Box>
        ) : (
          <List disablePadding>
            {messages.map((msg, index) => (
              <ListItem
                key={index}
                sx={{
                  display: "flex",
                  justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
                  px: 0,
                }}
              >
                <Paper
                  elevation={1}
                  sx={{
                    p: msg.role === "bot" ? 0 : "10px 15px",
                    bgcolor: msg.role === "user" ? "primary.main" : "#fff",
                    color: msg.role === "user" ? "primary.contrastText" : "text.primary",
                    borderBottomLeftRadius: msg.role === "user" ? "18px" : "4px",
                    borderBottomRightRadius: msg.role === "user" ? "4px" : "18px",
                    wordWrap: "break-word",
                  }}
                >
                  {msg.role === "bot" ? (
                    <Box
                      sx={{
                        p: "10px 15px",
                        lineHeight: 1.6,
                        "& p": { my: 0.5, lineHeight: "inherit" },
                        "& ul, & ol": { my: 0.5, pl: 2.5, lineHeight: "inherit" },
                        "& li": { mb: 0.2 },
                        "& pre": {
                          my: 1,
                          p: 1.5,
                          bgcolor: "#f0f0f0",
                          borderRadius: 1,
                          overflowX: "auto",
                        },
                        "& code": { fontSize: "0.9em", fontFamily: "monospace" },
                        "& table": { borderCollapse: "collapse", width: "100%", my: 1 },
                        "& th, & td": { border: "1px solid #ddd", p: 1, textAlign: "left" },
                        "& th": { bgcolor: "#f2f2f2", fontWeight: "bold" },
                      }}
                    >
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                    </Box>
                  ) : (
                    <Typography variant="body1" sx={{ whiteSpace: "pre-wrap", lineHeight: 1.6 }}>
                      {msg.content}
                    </Typography>
                  )}
                </Paper>
              </ListItem>
            ))}
          </List>
        )}
      </Box>

      {/* 입력 영역 */}
      <Box
        component="form"
        sx={{
          display: "flex",
          alignItems: "center",
          py: "15px", // 상하 패딩 유지 또는 조정
          px: { xs: 4, sm: 6, md: 8, lg: 15, xl: 20 }, // 메시지 목록과 동일한 좌우 패딩 적용
          borderTop: "1px solid #e0e0e0",
          bgcolor: "#f8f9fa",
          flexShrink: 0, // 입력 영역 높이 고정
        }}
        onSubmit={(e) => {
          e.preventDefault();
          handleSendMessage();
        }}
      >
        <TextField
          fullWidth
          variant="outlined"
          size="small"
          placeholder={sessionId ? "메시지를 입력하세요..." : "새 대화를 시작해주세요."}
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={!sessionId || sending || loadingHistory}
          multiline
          maxRows={4}
          sx={{
            mr: 1,
            "& .MuiOutlinedInput-root": {
              borderRadius: "20px",
              backgroundColor: "white",
            },
          }}
        />
        <IconButton
          color="primary"
          onClick={handleSendMessage}
          disabled={!sessionId || !inputMessage.trim() || sending || loadingHistory}
          sx={{ flexShrink: 0 }}
        >
          <SendIcon />
        </IconButton>
      </Box>
    </Box>
  );
};

export default ChatWindow;
