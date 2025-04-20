import { useState, useEffect, useCallback, useRef } from "react";
import { Box } from "@mui/material";
import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";
import { getSessions, getHistory, deleteSession } from "../services/api";
export interface Message {
  role: "user" | "assistant" | "bot"; // 'bot'은 프론트엔드 표시용
  content: string;
}
interface ApiMessage {
  role: string;
  content: string;
}

const ChatPage: React.FC = () => {
  const [sessionIds, setSessionIds] = useState<string[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loadingHistory, setLoadingHistory] = useState<boolean>(false);
  const isInitialized = useRef(false);

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

  // 새 세션 생성 함수 (Sidebar에서도 호출 가능하게 유지)
  const handleNewSession = useCallback((newSessionId: string) => {
    setSessionIds((prev) => [newSessionId, ...prev]); // 목록 맨 앞에 추가
    setActiveSessionId(newSessionId);
    localStorage.setItem("activeConversationId", newSessionId);
    setMessages([{ role: "bot", content: "새 대화를 시작합니다." }]); // 초기 메시지
  }, []); // 의존성 없음 (상태 업데이트 함수는 안정적)

  // 초기 로드: 세션 목록 로드 및 마지막 활성 세션 또는 첫 세션/새 세션 로드
  useEffect(() => {
    if (isInitialized.current) {
      return;
    }
    isInitialized.current = true;

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
        localStorage.setItem("activeConversationId", targetSessionId);
        await loadHistory(targetSessionId);
      } else {
        // 활성 세션이 없으면 자동으로 새 대화 시작
        console.log("활성 세션 없음 - 새 대화 자동 시작");
        const newSessionId = `conv_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
        handleNewSession(newSessionId); // 새 세션 처리 함수 호출
      }
    };
    initialize();
    // handleNewSession은 useCallback으로 생성되었고 의존성이 없으므로 안정적,
    // 명시적으로 추가해도 좋지만 필수는 아님. loadSessions/loadHistory는 이미 포함됨.
  }, [loadSessions, loadHistory, handleNewSession]); // handleNewSession 추가

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

  // 세션 삭제 처리 함수
  const handleDeleteSession = useCallback(
    async (sessionIdToDelete: string) => {
      try {
        await deleteSession(sessionIdToDelete); // API 호출

        // 상태 업데이트: 삭제된 세션 ID 제거
        setSessionIds((prev) => prev.filter((id) => id !== sessionIdToDelete));

        // 현재 활성 세션이 삭제된 세션인 경우 처리
        if (activeSessionId === sessionIdToDelete) {
          const remainingSessions = sessionIds.filter((id) => id !== sessionIdToDelete);
          if (remainingSessions.length > 0) {
            // 남은 세션 중 첫 번째(가장 최신) 세션을 활성화
            const newActiveId = remainingSessions[0];
            setActiveSessionId(newActiveId);
            localStorage.setItem("activeConversationId", newActiveId);
            await loadHistory(newActiveId); // 새 활성 세션 기록 로드
          } else {
            // 남은 세션이 없으면 활성 세션 null 처리 및 메시지 초기화
            setActiveSessionId(null);
            localStorage.removeItem("activeConversationId");
            setMessages([{ role: "bot", content: "대화를 선택하거나 새 대화를 시작하세요." }]);
          }
        } else {
          // 현재 활성 세션이 삭제되지 않았다면, 세션 목록만 업데이트하고 끝
        }
      } catch (error) {
        console.error("세션 삭제 처리 중 오류:", error);
        // 사용자에게 오류 알림 표시 (예: 스낵바 사용)
      }
    },
    [activeSessionId, sessionIds, loadHistory]
  ); // 의존성 추가

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
        onDeleteSession={handleDeleteSession}
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
