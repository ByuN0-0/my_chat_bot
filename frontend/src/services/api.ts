import axios from "axios";

// Axios 인스턴스 생성
const apiClient = axios.create({
  // Vite 프록시 설정에서 정의한 /api 접두사 사용
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

// --- 세션 관련 API ---

// 세션 목록 가져오기
export const getSessions = async () => {
  try {
    const response = await apiClient.get("/sessions");
    return response.data.sessions; // {sessions: [...]} 형태이므로 .sessions 접근
  } catch (error) {
    console.error("Error fetching sessions:", error);
    throw error; // 에러를 다시 throw하여 호출부에서 처리하도록 함
  }
};

// 특정 세션 기록 가져오기
export const getHistory = async (conversationId: string) => {
  try {
    const response = await apiClient.get(`/history/${conversationId}`);
    return response.data; // 기록 배열 직접 반환
  } catch (error) {
    console.error(`Error fetching history for ${conversationId}:`, error);
    throw error;
  }
};

// --- 채팅 관련 API ---

// 새 메시지 보내기
export const sendMessage = async (conversationId: string, message: string) => {
  try {
    const response = await apiClient.post("/chat", { conversation_id: conversationId, message });
    return response.data; // {response: "..."} 형태
  } catch (error) {
    console.error("Error sending message:", error);
    throw error;
  }
};

// --- 관리자 관련 API ---

// 일별 통계 가져오기
export const getDailyStats = async () => {
  try {
    const response = await apiClient.get("/admin/usage/daily");
    return response.data.daily_stats; // {daily_stats: [...]} 형태
  } catch (error) {
    console.error("Error fetching daily stats:", error);
    throw error;
  }
};

// 월별 통계 가져오기
export const getMonthlyStats = async () => {
  try {
    const response = await apiClient.get("/admin/usage/monthly");
    return response.data.monthly_stats; // {monthly_stats: [...]} 형태
  } catch (error) {
    console.error("Error fetching monthly stats:", error);
    throw error;
  }
};

export default apiClient;
