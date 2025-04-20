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

function formatCost(cost: number): string {
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
  // 총계 계산
  const totals = data?.reduce(
    (acc, stat) => {
      acc.prompt_tokens += stat.prompt_tokens;
      acc.completion_tokens += stat.completion_tokens;
      acc.cost += stat.cost;
      return acc;
    },
    { prompt_tokens: 0, completion_tokens: 0, cost: 0 }
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
            <TableCell align="right">예상 비용 (USD)</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((row) => {
            const period =
              type === "daily" ? (row as DailyUsageStat).date : (row as MonthlyUsageStat).month;
            const totalTokens = row.prompt_tokens + row.completion_tokens;
            return (
              <TableRow key={period} hover>
                <TableCell>{period}</TableCell>
                <TableCell align="right">{formatNumber(row.prompt_tokens)}</TableCell>
                <TableCell align="right">{formatNumber(row.completion_tokens)}</TableCell>
                <TableCell align="right">{formatNumber(totalTokens)}</TableCell>
                <TableCell align="right">{formatCost(row.cost)}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
        {totals && (
          <TableFooter sx={{ "& td": { fontWeight: "bold", bgcolor: "#eef2f7" } }}>
            <TableRow>
              <TableCell>{totalLabel}</TableCell>
              <TableCell align="right">{formatNumber(totals.prompt_tokens)}</TableCell>
              <TableCell align="right">{formatNumber(totals.completion_tokens)}</TableCell>
              <TableCell align="right">
                {formatNumber(totals.prompt_tokens + totals.completion_tokens)}
              </TableCell>
              <TableCell align="right">{formatCost(totals.cost)}</TableCell>
            </TableRow>
          </TableFooter>
        )}
      </Table>
    </TableContainer>
  );
};

export default StatsTable;
