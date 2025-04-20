import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  CircularProgress,
  Box,
  TableFooter,
} from "@mui/material";
import { DailyUsageStat, MonthlyUsageStat } from "../schemas/admin"; // 스키마 임포트

// 숫자 및 비용 포맷 함수 (AdminPage.html의 로직과 동일)
function formatNumber(num: number): string {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// 비용 포맷 함수 주석 해제 또는 다시 추가
function formatCost(cost: number): string {
  // 비용이 매우 작을 수 있으므로 소수점 아래 자릿수 조정 (예: 6자리)
  return `$${cost.toFixed(6)}`;
}

// Props 타입 정의
interface StatsTableProps {
  title: string;
  data: DailyUsageStat[] | MonthlyUsageStat[] | null;
  type: "daily" | "monthly";
  isLoading: boolean;
  error: Error | null; // any 대신 Error 타입 또는 null 사용
}

const StatsTable: React.FC<StatsTableProps> = ({ title, data, type, isLoading, error }) => {
  // 총계 계산 - cost 필드 추가
  const totals = data?.reduce(
    (acc, stat) => {
      acc.input_tokens += stat.input_tokens;
      acc.output_tokens += stat.output_tokens;
      acc.total_tokens += stat.total_tokens;
      acc.cost += stat.cost; // 비용 누적 추가
      return acc;
    },
    { input_tokens: 0, output_tokens: 0, total_tokens: 0, cost: 0 } // 초기값에 cost 추가
  );

  const periodLabel = type === "daily" ? "날짜" : "월";
  const totalLabel = type === "daily" ? "일별 총계" : "월별 총계";

  if (isLoading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", my: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Paper sx={{ p: 2, mt: 2, mb: 2 }}>
        <Typography color="error">
          {title} 로딩 중 에러 발생: {error.message}
        </Typography>
      </Paper>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Typography sx={{ textAlign: "center", my: 4, color: "text.secondary" }}>
        표시할 데이터가 없습니다.
      </Typography>
    );
  }

  return (
    <TableContainer component={Paper} sx={{ my: 3 }}>
      <Typography variant="h6" sx={{ p: 2 }}>
        {title}
      </Typography>
      <Table size="small">
        <TableHead>
          <TableRow sx={{ "& th": { fontWeight: "bold", bgcolor: "#f5f5f5" } }}>
            <TableCell>{periodLabel}</TableCell>
            <TableCell align="right">입력 토큰</TableCell>
            <TableCell align="right">출력 토큰</TableCell>
            <TableCell align="right">총 토큰</TableCell>
            <TableCell align="right">예상 비용 (USD)</TableCell> {/* 비용 열 복구 */}
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((row) => {
            const period =
              type === "daily" ? (row as DailyUsageStat).date : (row as MonthlyUsageStat).month;
            return (
              <TableRow key={period} hover>
                <TableCell>{period}</TableCell>
                <TableCell align="right">{formatNumber(row.input_tokens)}</TableCell>
                <TableCell align="right">{formatNumber(row.output_tokens)}</TableCell>
                <TableCell align="right">{formatNumber(row.total_tokens)}</TableCell>
                <TableCell align="right">{formatCost(row.cost)}</TableCell> {/* 비용 셀 복구 */}
              </TableRow>
            );
          })}
        </TableBody>
        {totals && (
          <TableFooter sx={{ "& td": { fontWeight: "bold", bgcolor: "#eef2f7" } }}>
            <TableRow>
              <TableCell>{totalLabel}</TableCell>
              <TableCell align="right">{formatNumber(totals.input_tokens)}</TableCell>
              <TableCell align="right">{formatNumber(totals.output_tokens)}</TableCell>
              <TableCell align="right">{formatNumber(totals.total_tokens)}</TableCell>
              <TableCell align="right">{formatCost(totals.cost)}</TableCell> {/* 비용 셀 복구 */}
            </TableRow>
          </TableFooter>
        )}
      </Table>
    </TableContainer>
  );
};

export default StatsTable;
