import React, { useState, useEffect } from "react";
import { Typography, Paper, Grid, Box, Button } from "@mui/material"; // Button 추가
import { Link } from "react-router-dom"; // Link 추가
import StatsTable from "../components/StatsTable"; // StatsTable 컴포넌트 임포트
import { getDailyStats, getMonthlyStats } from "../services/api"; // API 서비스 임포트
import { DailyUsageStat, MonthlyUsageStat } from "../schemas/admin"; // 스키마 임포트 (경로 확인 필요)

// 관리자 페이지 CSS 임포트 (경로 확인)
import "../admin.css";

const AdminPage: React.FC = () => {
  // 일별 통계 상태
  const [dailyData, setDailyData] = useState<DailyUsageStat[] | null>(null);
  const [dailyLoading, setDailyLoading] = useState<boolean>(true);
  const [dailyError, setDailyError] = useState<Error | null>(null); // any 대신 Error | null

  // 월별 통계 상태
  const [monthlyData, setMonthlyData] = useState<MonthlyUsageStat[] | null>(null);
  const [monthlyLoading, setMonthlyLoading] = useState<boolean>(true);
  const [monthlyError, setMonthlyError] = useState<Error | null>(null); // any 대신 Error | null

  // 데이터 로딩 useEffect
  useEffect(() => {
    const fetchData = async () => {
      // 일별 통계 데이터 로딩
      setDailyLoading(true);
      setDailyError(null);
      try {
        const dailyStats = await getDailyStats();
        setDailyData(dailyStats);
      } catch (err) {
        if (err instanceof Error) {
          setDailyError(err);
        } else {
          setDailyError(new Error("An unknown error occurred"));
        }
      } finally {
        setDailyLoading(false);
      }

      // 월별 통계 데이터 로딩
      setMonthlyLoading(true);
      setMonthlyError(null);
      try {
        const monthlyStats = await getMonthlyStats();
        setMonthlyData(monthlyStats);
      } catch (err) {
        if (err instanceof Error) {
          setMonthlyError(err);
        } else {
          setMonthlyError(new Error("An unknown error occurred"));
        }
      } finally {
        setMonthlyLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
        <Typography variant="h4" gutterBottom component="div">
          관리자 페이지 - 사용 통계
        </Typography>
        <Button component={Link} to="/" variant="outlined">
          챗봇 페이지로 돌아가기
        </Button>
      </Box>
      <Grid container spacing={3}>
        <Box sx={{ width: "100%", mb: 2 }}>
          {/* 일별 통계 테이블 */}
          <StatsTable
            title="일별 사용량 통계"
            data={dailyData}
            type="daily"
            isLoading={dailyLoading}
            error={dailyError}
          />
        </Box>
        <Box sx={{ width: "100%" }}>
          {/* 월별 통계 테이블 */}
          <StatsTable
            title="월별 사용량 통계"
            data={monthlyData}
            type="monthly"
            isLoading={monthlyLoading}
            error={monthlyError}
          />
        </Box>
      </Grid>
    </Paper>
  );
};

export default AdminPage;
