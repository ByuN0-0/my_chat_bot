import {
  Box,
  Button,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Divider,
  Link as MuiLink,
  IconButton,
  Tooltip,
} from "@mui/material";
import {
  AddCommentOutlined,
  ForumOutlined,
  AdminPanelSettingsOutlined,
  DeleteOutline,
} from "@mui/icons-material";
import { Link } from "react-router-dom";

interface SidebarProps {
  sessionIds: string[];
  activeSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onNewSession: (newSessionId: string) => void;
  onDeleteSession: (sessionId: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  sessionIds,
  activeSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
}) => {
  const handleNewChatClick = () => {
    // ChatPage에서 정의한 새 세션 생성 로직 호출
    // 이 함수는 내부적으로 새 ID 생성 및 상태 업데이트를 수행
    const newSessionId = `conv_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    onNewSession(newSessionId);
  };

  const handleDeleteClick = (event: React.MouseEvent<HTMLButtonElement>, sessionId: string) => {
    event.stopPropagation(); // 이벤트 버블링 중단 (ListItemButton 클릭 방지)
    if (window.confirm(`대화 '${sessionId.substring(5, 15)}...' 를 정말 삭제하시겠습니까?`)) {
      onDeleteSession(sessionId);
    }
  };

  return (
    <Box
      sx={{
        width: "260px",
        flexShrink: 0, // 너비 고정
        height: "100%",
        borderRight: "1px solid #dee2e6",
        bgcolor: "#f8f9fa",
        display: "flex",
        flexDirection: "column",
        overflowY: "auto",
      }}
    >
      {/* 새 대화 버튼 */}
      <Box sx={{ p: 2 }}>
        <Button
          variant="contained"
          startIcon={<AddCommentOutlined />}
          fullWidth
          onClick={handleNewChatClick}
          sx={{ borderRadius: "8px", textTransform: "none", fontWeight: 500 }}
        >
          새 대화 시작
        </Button>
      </Box>

      <Divider />

      {/* 대화 목록 */}
      <Typography variant="overline" sx={{ px: 2, pt: 2, color: "text.secondary" }}>
        대화 목록
      </Typography>
      <List sx={{ flexGrow: 1, overflowY: "auto", px: 1 }}>
        {sessionIds.length === 0 && (
          <Typography variant="body2" sx={{ textAlign: "center", color: "text.secondary", mt: 2 }}>
            대화 기록이 없습니다.
          </Typography>
        )}
        {sessionIds.map((sessionId) => (
          <ListItemButton
            key={sessionId}
            selected={sessionId === activeSessionId}
            onClick={() => onSelectSession(sessionId)}
            sx={{
              borderRadius: "6px",
              mb: 0.5,
              pr: 1,
              display: "flex",
              justifyContent: "space-between",
              "&:hover .delete-button": {
                opacity: 1,
              },
            }}
          >
            <Box sx={{ display: "flex", alignItems: "center", overflow: "hidden" }}>
              <ListItemIcon sx={{ minWidth: "36px" }}>
                <ForumOutlined fontSize="small" />
              </ListItemIcon>
              <ListItemText
                primary={`대화 ${sessionId.substring(5, 15)}...`}
                primaryTypographyProps={{
                  fontSize: "0.9em",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
                title={sessionId}
                sx={{ mr: 1 }}
              />
            </Box>
            <Tooltip title="대화 삭제">
              <IconButton
                className="delete-button"
                size="small"
                onClick={(e) => handleDeleteClick(e, sessionId)}
                sx={{
                  opacity: 0,
                  transition: "opacity 0.2s ease-in-out",
                  "&:hover": {
                    backgroundColor: "action.hover",
                  },
                }}
                aria-label={`대화 ${sessionId} 삭제`}
              >
                <DeleteOutline fontSize="small" />
              </IconButton>
            </Tooltip>
          </ListItemButton>
        ))}
      </List>

      <Divider />

      {/* 관리자 페이지 링크 영역 */}
      <Box
        sx={{
          p: "15px 20px", // 수정: 입력 영역과 동일한 패딩 적용 (상하 15px, 좌우 20px)
          mt: "auto",
          borderTop: "1px solid #dee2e6", // 사이드바 경계선 색상 유지
        }}
      >
        <MuiLink
          component={Link}
          to="/admin"
          sx={{
            display: "flex",
            alignItems: "center",
            textDecoration: "none",
            color: "text.secondary",
            p: 1,
            borderRadius: "6px",
            "&:hover": {
              backgroundColor: "action.hover",
            },
          }}
        >
          <AdminPanelSettingsOutlined sx={{ mr: 1.5 }} />
          <Typography variant="body2">관리자 페이지</Typography>
        </MuiLink>
      </Box>
    </Box>
  );
};

export default Sidebar;
