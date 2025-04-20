/**
 * 일별 사용량 통계 데이터 타입
 */
export interface DailyUsageStat {
  date: string; // 날짜 (YYYY-MM-DD 형식)
  prompt_tokens: number; // 입력 토큰 수
  completion_tokens: number; // 출력 토큰 수
  cost: number; // 비용
}

/**
 * 월별 사용량 통계 데이터 타입
 */
export interface MonthlyUsageStat {
  month: string; // 월 (YYYY-MM 형식)
  prompt_tokens: number; // 입력 토큰 수
  completion_tokens: number; // 출력 토큰 수
  cost: number; // 비용
}
