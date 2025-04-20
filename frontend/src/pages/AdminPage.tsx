import { Box, Typography, Container, Link as MuiLink } from "@mui/material"; // MUI 컴포넌트 사용
import { Link } from "react-router-dom"; // 페이지 이동을 위한 Link

// 필요한 컴포넌트들 (나중에 생성)
// import StatsTable from '../components/StatsTable';

// 관리자 페이지 CSS 임포트
import "../admin.css";

const AdminPage: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Link 컴포넌트를 사용하여 내부 라우팅 */}
      <MuiLink component={Link} to="/" variant="body2" sx={{ mb: 2, display: "inline-block" }}>
        &larr; 채팅 페이지로 돌아가기
      </MuiLink>
      <Typography component="h1" variant="h4" gutterBottom>
        챗봇 사용량 통계
      </Typography>

      {/* 일별 통계 섹션 (임시) */}
      <Box sx={{ my: 4 }}>
        <Typography component="h2" variant="h5" gutterBottom>
          일별 사용량
        </Typography>
        <Typography>일별 통계 테이블이 여기에 표시됩니다.</Typography>
        {/* <StatsTable type="daily" /> */}
      </Box>

      {/* 월별 통계 섹션 (임시) */}
      <Box sx={{ my: 4 }}>
        <Typography component="h2" variant="h5" gutterBottom>
          월별 사용량
        </Typography>
        <Typography>월별 통계 테이블이 여기에 표시됩니다.</Typography>
        {/* <StatsTable type="monthly" /> */}
      </Box>
    </Container>
  );
};

export default AdminPage;
