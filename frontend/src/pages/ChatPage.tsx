import { useState, useEffect, useCallback } from "react";
import { Box } from "@mui/material";

// 컴포넌트 임포트 (다음 단계에서 생성)
import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";

// API 서비스 임포트
import { getSessions, getHistory } from "../services/api";

// 메시지 타입 정의 (선택 사항이지만 권장)
export interface Message {
  role: "user" | "assistant" | "bot"; // 'bot'은 프론트엔드 표시용
  content: string;
}

// API 응답의 메시지 타입 정의 (백엔드 API와 일치해야 함)
interface ApiMessage {
  role: string;
  content: string;
  // 백엔드가 다른 필드도 반환한다면 여기에 추가
}

const ChatPage: React.FC = () => {
  const [sessionIds, setSessionIds] = useState<string[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loadingHistory, setLoadingHistory] = useState<boolean>(false);

  // 세션 목록 로드 함수
  const loadSessions = useCallback(async () => {
    try {
      const fetchedSessionIds = await getSessions();
      setSessionIds(fetchedSessionIds || []);
      console.log("세션 목록 로드 완료:", fetchedSessionIds);
      return fetchedSessionIds || [];
    } catch (error) {
      console.error("세션 목록 로드 실패:", error);
      setSessionIds([]); // 에러 시 빈 배열로 초기화
      return [];
    }
  }, []);

  // 대화 기록 로드 함수
  const loadHistory = useCallback(async (sessionId: string) => {
    if (!sessionId) return;
    setLoadingHistory(true);
    setMessages([{ role: "bot", content: `대화 (${sessionId.substring(5, 15)}...) 로딩 중...` }]);
    try {
      // getHistory의 반환 타입을 명시하거나, 여기서 타입을 단언 (as 사용)
      const historyData: ApiMessage[] = await getHistory(sessionId);
      const formattedHistory: Message[] = historyData.map((msg) => ({
        // msg 타입이 이제 ApiMessage로 추론됨
        role: msg.role === "assistant" ? "bot" : (msg.role as "user" | "assistant"), // 타입 단언 추가
        content: msg.content,
      }));
      setMessages(formattedHistory);
      console.log("대화 기록 로드 완료:", sessionId, formattedHistory);
    } catch (error) {
      console.error("대화 기록 로드 실패:", error);
      setMessages([{ role: "bot", content: "대화 기록 로딩 중 오류가 발생했습니다." }]);
    } finally {
      setLoadingHistory(false);
    }
  }, []);

  // 초기 로드: 세션 목록 로드 및 마지막 활성 세션 또는 첫 세션 로드
  useEffect(() => {
    const initialize = async () => {
      const loadedSessions = await loadSessions();
      const lastActiveId = localStorage.getItem("activeConversationId");

      let targetSessionId: string | null = null;
      if (lastActiveId && loadedSessions.includes(lastActiveId)) {
        targetSessionId = lastActiveId;
      } else if (loadedSessions.length > 0) {
        targetSessionId = loadedSessions[0]; // 최신 세션
      }

      if (targetSessionId) {
        setActiveSessionId(targetSessionId);
        localStorage.setItem("activeConversationId", targetSessionId); // 로컬 스토리지 업데이트
        await loadHistory(targetSessionId);
      } else {
        // 세션이 하나도 없으면 새 세션 생성 로직 호출 (Sidebar에서 구현)
        // 여기서는 일단 null 상태 유지
        console.log("활성 세션 없음");
      }
    };
    initialize();
  }, [loadSessions, loadHistory]); // 의존성 배열에 함수 추가

  // 세션 전환 함수
  const handleSelectSession = useCallback(
    async (sessionId: string) => {
      if (sessionId === activeSessionId) return;
      setActiveSessionId(sessionId);
      localStorage.setItem("activeConversationId", sessionId);
      await loadHistory(sessionId);
    },
    [activeSessionId, loadHistory]
  );

  // 새 세션 생성 함수 (Sidebar에서 호출)
  const handleNewSession = useCallback((newSessionId: string) => {
    setSessionIds((prev) => [newSessionId, ...prev]); // 목록 맨 앞에 추가
    setActiveSessionId(newSessionId);
    localStorage.setItem("activeConversationId", newSessionId);
    setMessages([{ role: "bot", content: "새 대화를 시작합니다." }]); // 초기 메시지
  }, []);

  // 메시지 목록 업데이트 함수 (ChatWindow에서 호출)
  const addMessageToList = (message: Message) => {
    setMessages((prev) => [...prev, message]);
  };

  return (
    <Box sx={{ display: "flex", width: "100%", height: "100vh" }}>
      <Sidebar
        sessionIds={sessionIds}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewSession={handleNewSession}
      />
      <ChatWindow
        sessionId={activeSessionId}
        messages={messages}
        loadingHistory={loadingHistory}
        addMessageToList={addMessageToList}
      />
    </Box>
  );
};

export default ChatPage;
