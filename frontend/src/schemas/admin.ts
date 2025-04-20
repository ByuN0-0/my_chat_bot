/**
 * 일별 사용량 통계 데이터 타입
 */
export interface DailyUsageStat {
  date: string; // 날짜 (YYYY-MM-DD 형식)
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  cost: number;
}

/**
 * 월별 사용량 통계 데이터 타입
 */
export interface MonthlyUsageStat {
  month: string; // 월 (YYYY-MM 형식)
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  cost: number;
}
