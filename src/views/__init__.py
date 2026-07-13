from .auth_view import build_auth_view
from .dashboard_view import build_dashboard_view
from .create_match_view import build_create_match_view
from .match_detail_view import build_match_detail_view
from .profile_view import build_profile_view

__all__ = [
    "build_auth_view",
    "build_dashboard_view",
    "build_create_match_view",
    "build_match_detail_view",
    "build_profile_view",
]
