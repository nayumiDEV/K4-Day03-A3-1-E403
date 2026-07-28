"""
Offline tool registry for the career-guidance ReAct Agent.

The module intentionally uses curated local demo data. Public tools are deterministic,
have no network dependency, do not write user data, and return JSON strings with a
shared response contract so their results can be inserted into an Agent Observation.
"""

from __future__ import annotations

import difflib
import json
import re
import unicodedata
from typing import Any


CATALOG_VERSION = "2.0-demo"
ASSESSMENT_VERSION = "riasec-demo-v1"
LOCAL_SOURCE = "curated_local_demo_data"


# required_level uses a 1-5 scale; importance uses a 1-5 scale.
CAREER_CATALOG: dict[str, dict[str, Any]] = {
    "data-analyst": {
        "display_name": "Data Analyst",
        "aliases": ["data analyst", "chuyên viên phân tích dữ liệu"],
        "description": (
            "Thu thập, làm sạch và phân tích dữ liệu để hỗ trợ các quyết định "
            "kinh doanh."
        ),
        "riasec": ["I", "C"],
        "interest_keywords": [
            "dữ liệu",
            "phân tích",
            "số liệu",
            "logic",
            "biểu đồ",
        ],
        "goal_keywords": ["data", "báo cáo", "insight", "kinh doanh"],
        "work_preferences": ["phân tích", "quy trình", "làm việc độc lập"],
        "required_skills": [
            {
                "name": "Excel",
                "category": "technical",
                "required_level": 3,
                "importance": 4,
            },
            {
                "name": "SQL",
                "category": "technical",
                "required_level": 3,
                "importance": 5,
            },
            {
                "name": "Python",
                "category": "technical",
                "required_level": 2,
                "importance": 4,
            },
            {
                "name": "Thống kê",
                "category": "knowledge",
                "required_level": 3,
                "importance": 5,
            },
            {
                "name": "Trực quan hóa dữ liệu",
                "category": "technical",
                "required_level": 3,
                "importance": 4,
            },
        ],
        "common_tasks": [
            "Làm sạch và kiểm tra chất lượng dữ liệu",
            "Viết truy vấn SQL",
            "Xây dựng dashboard và báo cáo",
            "Trình bày insight cho các bên liên quan",
        ],
        "education_paths": [
            "Hệ thống thông tin",
            "Khoa học dữ liệu",
            "Thống kê",
            "Kinh tế",
        ],
        "related_roles": ["Business Analyst", "AI Engineer", "Product Manager"],
    },
    "ai-engineer": {
        "display_name": "AI Engineer",
        "aliases": [
            "ai engineer",
            "kỹ sư ai",
            "kỹ sư trí tuệ nhân tạo",
            "machine learning engineer",
        ],
        "description": (
            "Thiết kế, huấn luyện, đánh giá và triển khai các hệ thống học máy "
            "giải quyết bài toán thực tế."
        ),
        "riasec": ["I", "R"],
        "interest_keywords": [
            "ai",
            "trí tuệ nhân tạo",
            "học máy",
            "nghiên cứu",
            "thuật toán",
            "dữ liệu",
        ],
        "goal_keywords": ["ai", "machine learning", "mô hình", "tự động hóa"],
        "work_preferences": ["nghiên cứu", "kỹ thuật", "thử nghiệm"],
        "required_skills": [
            {
                "name": "Python",
                "category": "technical",
                "required_level": 4,
                "importance": 5,
            },
            {
                "name": "Machine Learning",
                "category": "technical",
                "required_level": 4,
                "importance": 5,
            },
            {
                "name": "Deep Learning",
                "category": "technical",
                "required_level": 3,
                "importance": 4,
            },
            {
                "name": "Toán và thống kê",
                "category": "knowledge",
                "required_level": 3,
                "importance": 5,
            },
            {
                "name": "Git",
                "category": "technical",
                "required_level": 3,
                "importance": 3,
            },
        ],
        "common_tasks": [
            "Chuẩn bị và khám phá dữ liệu",
            "Huấn luyện và đánh giá mô hình",
            "Xây dựng pipeline suy luận",
            "Theo dõi chất lượng mô hình sau triển khai",
        ],
        "education_paths": [
            "Khoa học máy tính",
            "Khoa học dữ liệu",
            "Toán tin",
            "Trí tuệ nhân tạo",
        ],
        "related_roles": ["Data Analyst", "Backend Developer", "Data Scientist"],
    },
    "backend-developer": {
        "display_name": "Backend Developer",
        "aliases": ["backend developer", "backend", "lập trình viên backend"],
        "description": (
            "Xây dựng API, xử lý nghiệp vụ và quản lý dữ liệu phía máy chủ."
        ),
        "riasec": ["I", "R"],
        "interest_keywords": [
            "lập trình",
            "hệ thống",
            "logic",
            "api",
            "server",
        ],
        "goal_keywords": ["backend", "phần mềm", "web", "hệ thống"],
        "work_preferences": ["kỹ thuật", "giải quyết vấn đề", "làm việc nhóm"],
        "required_skills": [
            {
                "name": "Python",
                "category": "technical",
                "required_level": 3,
                "importance": 4,
            },
            {
                "name": "Cơ sở dữ liệu",
                "category": "technical",
                "required_level": 3,
                "importance": 5,
            },
            {
                "name": "REST API",
                "category": "technical",
                "required_level": 3,
                "importance": 5,
            },
            {
                "name": "Git",
                "category": "technical",
                "required_level": 3,
                "importance": 4,
            },
            {
                "name": "Kiểm thử phần mềm",
                "category": "technical",
                "required_level": 2,
                "importance": 3,
            },
        ],
        "common_tasks": [
            "Thiết kế và triển khai API",
            "Xây dựng logic nghiệp vụ",
            "Làm việc với cơ sở dữ liệu",
            "Kiểm thử và tối ưu hiệu năng hệ thống",
        ],
        "education_paths": [
            "Khoa học máy tính",
            "Kỹ thuật phần mềm",
            "Hệ thống thông tin",
        ],
        "related_roles": ["AI Engineer", "QA Engineer", "Cybersecurity Analyst"],
    },
    "ui-ux-designer": {
        "display_name": "UI/UX Designer",
        "aliases": [
            "ui ux designer",
            "ui/ux designer",
            "ux designer",
            "ui designer",
        ],
        "description": (
            "Nghiên cứu người dùng và thiết kế trải nghiệm cho các sản phẩm số."
        ),
        "riasec": ["A", "S"],
        "interest_keywords": [
            "thiết kế",
            "sáng tạo",
            "người dùng",
            "mỹ thuật",
            "trải nghiệm",
        ],
        "goal_keywords": ["ui", "ux", "thiết kế", "sản phẩm"],
        "work_preferences": ["sáng tạo", "giao tiếp", "làm việc nhóm"],
        "required_skills": [
            {
                "name": "Figma",
                "category": "technical",
                "required_level": 3,
                "importance": 4,
            },
            {
                "name": "User Research",
                "category": "technical",
                "required_level": 3,
                "importance": 5,
            },
            {
                "name": "Wireframing",
                "category": "technical",
                "required_level": 3,
                "importance": 4,
            },
            {
                "name": "Prototyping",
                "category": "technical",
                "required_level": 3,
                "importance": 4,
            },
            {
                "name": "Thiết kế giao diện",
                "category": "technical",
                "required_level": 3,
                "importance": 5,
            },
        ],
        "common_tasks": [
            "Nghiên cứu nhu cầu người dùng",
            "Xây dựng user flow và wireframe",
            "Thiết kế prototype",
            "Kiểm thử khả năng sử dụng",
        ],
        "education_paths": [
            "Thiết kế đồ họa",
            "Thiết kế tương tác",
            "Truyền thông đa phương tiện",
        ],
        "related_roles": ["Product Manager", "Digital Marketing Specialist"],
    },
    "product-manager": {
        "display_name": "Product Manager",
        "aliases": ["product manager", "quản lý sản phẩm", "product owner"],
        "description": (
            "Xác định vấn đề sản phẩm, ưu tiên tính năng và phối hợp các nhóm để "
            "tạo ra giá trị cho người dùng."
        ),
        "riasec": ["E", "S", "C"],
        "interest_keywords": [
            "sản phẩm",
            "kinh doanh",
            "giao tiếp",
            "chiến lược",
            "người dùng",
        ],
        "goal_keywords": ["product", "quản lý", "sản phẩm", "chiến lược"],
        "work_preferences": ["lãnh đạo", "giao tiếp", "làm việc nhóm"],
        "required_skills": [
            {
                "name": "Product Discovery",
                "category": "technical",
                "required_level": 3,
                "importance": 5,
            },
            {
                "name": "Phân tích dữ liệu",
                "category": "technical",
                "required_level": 2,
                "importance": 4,
            },
            {
                "name": "Giao tiếp",
                "category": "soft",
                "required_level": 4,
                "importance": 5,
            },
            {
                "name": "Ưu tiên công việc",
                "category": "soft",
                "required_level": 4,
                "importance": 5,
            },
            {
                "name": "Agile",
                "category": "knowledge",
                "required_level": 3,
                "importance": 3,
            },
        ],
        "common_tasks": [
            "Nghiên cứu vấn đề của người dùng",
            "Xây dựng product roadmap",
            "Ưu tiên yêu cầu sản phẩm",
            "Phối hợp với thiết kế và kỹ thuật",
        ],
        "education_paths": [
            "Quản trị kinh doanh",
            "Hệ thống thông tin",
            "Kỹ thuật phần mềm",
        ],
        "related_roles": ["Business Analyst", "UI/UX Designer", "Data Analyst"],
    },
    "business-analyst": {
        "display_name": "Business Analyst",
        "aliases": ["business analyst", "ba", "chuyên viên phân tích nghiệp vụ"],
        "description": (
            "Phân tích nhu cầu kinh doanh và chuyển chúng thành yêu cầu rõ ràng "
            "cho các nhóm sản phẩm và kỹ thuật."
        ),
        "riasec": ["I", "C", "S"],
        "interest_keywords": [
            "nghiệp vụ",
            "quy trình",
            "phân tích",
            "giao tiếp",
            "tài liệu",
        ],
        "goal_keywords": ["business", "nghiệp vụ", "quy trình", "sản phẩm"],
        "work_preferences": ["phân tích", "giao tiếp", "quy trình"],
        "required_skills": [
            {
                "name": "Phân tích yêu cầu",
                "category": "technical",
                "required_level": 4,
                "importance": 5,
            },
            {
                "name": "Mô hình hóa quy trình",
                "category": "technical",
                "required_level": 3,
                "importance": 4,
            },
            {
                "name": "SQL",
                "category": "technical",
                "required_level": 2,
                "importance": 3,
            },
            {
                "name": "Giao tiếp",
                "category": "soft",
                "required_level": 4,
                "importance": 5,
            },
            {
                "name": "Viết tài liệu",
                "category": "soft",
                "required_level": 4,
                "importance": 4,
            },
        ],
        "common_tasks": [
            "Phỏng vấn và làm rõ yêu cầu",
            "Mô hình hóa quy trình nghiệp vụ",
            "Viết đặc tả và tiêu chí nghiệm thu",
            "Phối hợp giữa người dùng và nhóm kỹ thuật",
        ],
        "education_paths": [
            "Hệ thống thông tin",
            "Quản trị kinh doanh",
            "Kinh tế",
        ],
        "related_roles": ["Product Manager", "Data Analyst", "QA Engineer"],
    },
    "cybersecurity-analyst": {
        "display_name": "Cybersecurity Analyst",
        "aliases": [
            "cybersecurity analyst",
            "security analyst",
            "chuyên viên an ninh mạng",
        ],
        "description": (
            "Giám sát, phân tích và ứng phó với các rủi ro an toàn thông tin."
        ),
        "riasec": ["I", "R", "C"],
        "interest_keywords": [
            "bảo mật",
            "an ninh mạng",
            "điều tra",
            "hệ thống",
            "rủi ro",
        ],
        "goal_keywords": ["security", "bảo mật", "an toàn thông tin"],
        "work_preferences": ["kỹ thuật", "quy trình", "giải quyết vấn đề"],
        "required_skills": [
            {
                "name": "Network Security",
                "category": "technical",
                "required_level": 3,
                "importance": 5,
            },
            {
                "name": "Linux",
                "category": "technical",
                "required_level": 3,
                "importance": 4,
            },
            {
                "name": "SIEM",
                "category": "technical",
                "required_level": 3,
                "importance": 4,
            },
            {
                "name": "Incident Response",
                "category": "technical",
                "required_level": 3,
                "importance": 5,
            },
            {
                "name": "Python",
                "category": "technical",
                "required_level": 2,
                "importance": 3,
            },
        ],
        "common_tasks": [
            "Theo dõi cảnh báo bảo mật",
            "Phân tích sự kiện và nhật ký hệ thống",
            "Điều tra và xử lý sự cố",
            "Đề xuất biện pháp giảm thiểu rủi ro",
        ],
        "education_paths": [
            "An toàn thông tin",
            "Mạng máy tính",
            "Khoa học máy tính",
        ],
        "related_roles": ["Backend Developer", "QA Engineer"],
    },
    "digital-marketing-specialist": {
        "display_name": "Digital Marketing Specialist",
        "aliases": [
            "digital marketing specialist",
            "digital marketer",
            "chuyên viên marketing số",
        ],
        "description": (
            "Lập kế hoạch, triển khai và đo lường các hoạt động tiếp thị trên "
            "các kênh số."
        ),
        "riasec": ["E", "A", "S"],
        "interest_keywords": [
            "marketing",
            "nội dung",
            "sáng tạo",
            "truyền thông",
            "kinh doanh",
        ],
        "goal_keywords": ["marketing", "thương hiệu", "quảng cáo", "nội dung"],
        "work_preferences": ["sáng tạo", "giao tiếp", "nhịp độ nhanh"],
        "required_skills": [
            {
                "name": "Content Marketing",
                "category": "technical",
                "required_level": 3,
                "importance": 5,
            },
            {
                "name": "SEO",
                "category": "technical",
                "required_level": 3,
                "importance": 4,
            },
            {
                "name": "Phân tích dữ liệu",
                "category": "technical",
                "required_level": 2,
                "importance": 4,
            },
            {
                "name": "Social Media",
                "category": "technical",
                "required_level": 3,
                "importance": 4,
            },
            {
                "name": "Giao tiếp",
                "category": "soft",
                "required_level": 4,
                "importance": 4,
            },
        ],
        "common_tasks": [
            "Lập kế hoạch nội dung",
            "Triển khai chiến dịch trên các kênh số",
            "Theo dõi chỉ số hiệu quả",
            "Tối ưu thông điệp và đối tượng mục tiêu",
        ],
        "education_paths": [
            "Marketing",
            "Truyền thông",
            "Quản trị kinh doanh",
        ],
        "related_roles": ["UI/UX Designer", "Product Manager", "Data Analyst"],
    },
    "qa-engineer": {
        "display_name": "QA Engineer",
        "aliases": [
            "qa engineer",
            "software tester",
            "tester",
            "kỹ sư kiểm thử phần mềm",
        ],
        "description": (
            "Thiết kế và thực hiện hoạt động kiểm thử nhằm bảo đảm chất lượng "
            "sản phẩm phần mềm."
        ),
        "riasec": ["C", "I", "R"],
        "interest_keywords": [
            "kiểm thử",
            "chất lượng",
            "chi tiết",
            "phần mềm",
            "quy trình",
        ],
        "goal_keywords": ["qa", "tester", "kiểm thử", "chất lượng"],
        "work_preferences": ["quy trình", "chi tiết", "làm việc nhóm"],
        "required_skills": [
            {
                "name": "Kiểm thử phần mềm",
                "category": "technical",
                "required_level": 4,
                "importance": 5,
            },
            {
                "name": "Test Automation",
                "category": "technical",
                "required_level": 3,
                "importance": 4,
            },
            {
                "name": "API Testing",
                "category": "technical",
                "required_level": 3,
                "importance": 4,
            },
            {
                "name": "SQL",
                "category": "technical",
                "required_level": 2,
                "importance": 3,
            },
            {
                "name": "Viết tài liệu",
                "category": "soft",
                "required_level": 3,
                "importance": 3,
            },
        ],
        "common_tasks": [
            "Phân tích yêu cầu và thiết kế test case",
            "Thực hiện kiểm thử thủ công và tự động",
            "Ghi nhận và theo dõi lỗi",
            "Đánh giá chất lượng trước khi phát hành",
        ],
        "education_paths": [
            "Kỹ thuật phần mềm",
            "Công nghệ thông tin",
            "Hệ thống thông tin",
        ],
        "related_roles": [
            "Backend Developer",
            "Business Analyst",
            "Cybersecurity Analyst",
        ],
    },
}


SKILL_ALIASES: dict[str, list[str]] = {
    "python": ["python", "python cơ bản", "lập trình python"],
    "sql": ["sql", "truy vấn sql"],
    "excel": ["excel", "microsoft excel"],
    "machine learning": ["machine learning", "ml", "học máy"],
    "deep learning": ["deep learning", "dl", "học sâu"],
    "toán và thống kê": ["toán và thống kê", "toán", "xác suất thống kê"],
    "thống kê": ["thống kê", "statistics"],
    "cơ sở dữ liệu": ["cơ sở dữ liệu", "database", "db"],
    "rest api": ["rest api", "api", "web api"],
    "git": ["git", "github", "version control"],
    "figma": ["figma"],
    "giao tiếp": ["giao tiếp", "communication"],
    "phân tích dữ liệu": ["phân tích dữ liệu", "data analysis"],
    "kiểm thử phần mềm": ["kiểm thử phần mềm", "software testing", "testing"],
    "viết tài liệu": ["viết tài liệu", "documentation"],
}


RIASEC_DIMENSIONS: dict[str, dict[str, str]] = {
    "R": {
        "name": "Realistic",
        "label": "Kỹ thuật - Thực hành",
        "description": "Ưa hoạt động thực tế, công cụ, máy móc và hệ thống.",
    },
    "I": {
        "name": "Investigative",
        "label": "Nghiên cứu - Phân tích",
        "description": "Ưa phân tích, khám phá và giải quyết vấn đề.",
    },
    "A": {
        "name": "Artistic",
        "label": "Nghệ thuật - Sáng tạo",
        "description": "Ưa sáng tạo, biểu đạt và thử nghiệm ý tưởng mới.",
    },
    "S": {
        "name": "Social",
        "label": "Xã hội - Hỗ trợ",
        "description": "Ưa hướng dẫn, hợp tác và hỗ trợ con người.",
    },
    "E": {
        "name": "Enterprising",
        "label": "Quản lý - Thuyết phục",
        "description": "Ưa lãnh đạo, thuyết phục và theo đuổi cơ hội.",
    },
    "C": {
        "name": "Conventional",
        "label": "Tổ chức - Quy trình",
        "description": "Ưa dữ liệu có cấu trúc, chi tiết và quy trình rõ ràng.",
    },
}


# These demo statements were written for this project and are not a clinical test.
RIASEC_QUESTION_BANK: tuple[dict[str, str], ...] = (
    {
        "question_id": "R1",
        "dimension": "R",
        "text": "Tôi thích lắp ráp, sửa chữa hoặc vận hành thiết bị.",
    },
    {
        "question_id": "R2",
        "dimension": "R",
        "text": "Tôi hứng thú với việc tạo ra một sản phẩm có thể sử dụng được.",
    },
    {
        "question_id": "R3",
        "dimension": "R",
        "text": "Tôi thích giải quyết vấn đề bằng cách trực tiếp thử và điều chỉnh.",
    },
    {
        "question_id": "I1",
        "dimension": "I",
        "text": "Tôi thích phân tích dữ liệu để tìm ra quy luật.",
    },
    {
        "question_id": "I2",
        "dimension": "I",
        "text": "Tôi thường muốn tìm hiểu nguyên nhân sâu xa của một vấn đề.",
    },
    {
        "question_id": "I3",
        "dimension": "I",
        "text": "Tôi hứng thú với các bài toán cần suy luận và kiểm chứng.",
    },
    {
        "question_id": "A1",
        "dimension": "A",
        "text": "Tôi thích tạo ra hình ảnh, nội dung hoặc trải nghiệm mới.",
    },
    {
        "question_id": "A2",
        "dimension": "A",
        "text": "Tôi thích công việc cho phép thử nhiều cách thể hiện khác nhau.",
    },
    {
        "question_id": "A3",
        "dimension": "A",
        "text": "Tôi thường nảy ra ý tưởng khác với cách làm quen thuộc.",
    },
    {
        "question_id": "S1",
        "dimension": "S",
        "text": "Tôi cảm thấy có động lực khi giúp người khác tiến bộ.",
    },
    {
        "question_id": "S2",
        "dimension": "S",
        "text": "Tôi thích lắng nghe và tìm hiểu nhu cầu của mọi người.",
    },
    {
        "question_id": "S3",
        "dimension": "S",
        "text": "Tôi thích hợp tác và chia sẻ kiến thức trong nhóm.",
    },
    {
        "question_id": "E1",
        "dimension": "E",
        "text": "Tôi tự tin trình bày và thuyết phục người khác về một ý tưởng.",
    },
    {
        "question_id": "E2",
        "dimension": "E",
        "text": "Tôi thích chủ động dẫn dắt một kế hoạch hoặc dự án.",
    },
    {
        "question_id": "E3",
        "dimension": "E",
        "text": "Tôi hứng thú với việc đặt mục tiêu và theo đuổi kết quả.",
    },
    {
        "question_id": "C1",
        "dimension": "C",
        "text": "Tôi thích sắp xếp thông tin theo hệ thống rõ ràng.",
    },
    {
        "question_id": "C2",
        "dimension": "C",
        "text": "Tôi chú ý đến chi tiết và thường kiểm tra lại công việc.",
    },
    {
        "question_id": "C3",
        "dimension": "C",
        "text": "Tôi làm việc hiệu quả khi có quy trình và tiêu chí cụ thể.",
    },
)


def _normalize_text(value: Any) -> str:
    """Normalize text for accent-insensitive and case-insensitive matching."""
    text = unicodedata.normalize("NFD", str(value or "").strip().lower())
    without_accents = "".join(
        character
        for character in text
        if unicodedata.category(character) != "Mn"
    )
    return re.sub(r"[^a-z0-9]+", " ", without_accents).strip()


def _normalize_items(value: Any) -> list[str]:
    """Convert a string or collection into a list of non-empty strings."""
    if isinstance(value, str):
        values = re.split(r"[,;\n]+", value)
    elif isinstance(value, dict):
        values = list(value)
    elif isinstance(value, (list, tuple, set)):
        values = list(value)
    else:
        return []
    return [str(item).strip() for item in values if str(item).strip()]


def _has_positive_gap(item: dict[str, Any]) -> bool:
    """Treat malformed gap values as actionable instead of raising an exception."""
    try:
        return int(item.get("gap", 1) or 0) > 0
    except (TypeError, ValueError):
        return True


def _extract_gap_skill_names(value: Any) -> list[str]:
    """Extract skill names from plain input or an analyze_skill_gap response."""
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith(("{", "[")):
            try:
                return _extract_gap_skill_names(json.loads(stripped))
            except json.JSONDecodeError:
                pass
        return _normalize_items(value)

    if isinstance(value, dict):
        for wrapper_key in ("data", "result"):
            nested = value.get(wrapper_key)
            if isinstance(nested, (dict, list, tuple)):
                extracted = _extract_gap_skill_names(nested)
                if extracted:
                    return extracted
        for gap_key in ("priority_gaps", "missing_skills", "skill_analysis"):
            nested = value.get(gap_key)
            if isinstance(nested, (dict, list, tuple)):
                extracted = _extract_gap_skill_names(nested)
                if extracted:
                    return extracted
        direct_name = value.get("skill") or value.get("name")
        if direct_name and _has_positive_gap(value):
            return [str(direct_name).strip()]
        return [
            str(skill_name).strip()
            for skill_name in value
            if str(skill_name).strip()
        ]

    if isinstance(value, (list, tuple, set)):
        skill_names = []
        for item in value:
            if isinstance(item, dict):
                direct_name = item.get("skill") or item.get("name")
                if direct_name and _has_positive_gap(item):
                    skill_names.append(str(direct_name).strip())
                elif not direct_name:
                    skill_names.extend(_extract_gap_skill_names(item))
            elif str(item).strip():
                skill_names.append(str(item).strip())
        return list(dict.fromkeys(skill_names))

    return []


def _metadata(
    *,
    source: str = LOCAL_SOURCE,
    confidence: float | None = None,
) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "source": source,
        "catalog_version": CATALOG_VERSION,
        "freshness": "static_demo",
    }
    if confidence is not None:
        metadata["confidence"] = round(max(0.0, min(1.0, confidence)), 2)
    return metadata


def _response(
    data: dict[str, Any],
    *,
    status: str = "success",
    warnings: list[str] | None = None,
    source: str = LOCAL_SOURCE,
    confidence: float | None = None,
) -> str:
    """Create the shared JSON response envelope used by all public tools."""
    return json.dumps(
        {
            "status": status,
            "data": data,
            "metadata": _metadata(source=source, confidence=confidence),
            "warnings": warnings or [],
        },
        ensure_ascii=False,
        indent=2,
    )


def _error(
    code: str,
    message: str,
    *,
    details: dict[str, Any] | None = None,
    retryable: bool = False,
) -> str:
    """Return a structured business error without crashing the Agent loop."""
    return json.dumps(
        {
            "status": "error",
            "error": {
                "code": code,
                "message": message,
                "retryable": retryable,
                "details": details or {},
            },
            "metadata": _metadata(),
            "warnings": [],
        },
        ensure_ascii=False,
        indent=2,
    )


def _career_search_text(career_id: str, career: dict[str, Any]) -> str:
    fields = [
        career_id,
        career["display_name"],
        career["description"],
        *career["aliases"],
        *career["interest_keywords"],
        *career["goal_keywords"],
    ]
    return " ".join(_normalize_text(field) for field in fields)


def _find_career(target_role: Any) -> tuple[str, dict[str, Any]] | None:
    """Resolve a career by ID, display name, alias, or a close textual match."""
    normalized_role = _normalize_text(target_role)
    if not normalized_role:
        return None

    candidates: dict[str, str] = {}
    for career_id, career in CAREER_CATALOG.items():
        names = [
            career_id,
            career["display_name"],
            *career["aliases"],
        ]
        normalized_names = {_normalize_text(name) for name in names}
        if normalized_role in normalized_names:
            return career_id, career
        if any(
            len(name) >= 4 and name in normalized_role
            for name in normalized_names
        ):
            return career_id, career
        for name in normalized_names:
            candidates[name] = career_id

    close_matches = difflib.get_close_matches(
        normalized_role,
        list(candidates),
        n=1,
        cutoff=0.82,
    )
    if not close_matches:
        return None
    career_id = candidates[close_matches[0]]
    return career_id, CAREER_CATALOG[career_id]


def _skill_alias_index() -> dict[str, str]:
    index: dict[str, str] = {}
    for canonical_name, aliases in SKILL_ALIASES.items():
        for alias in {canonical_name, *aliases}:
            index[_normalize_text(alias)] = canonical_name
    for career in CAREER_CATALOG.values():
        for skill in career["required_skills"]:
            normalized = _normalize_text(skill["name"])
            index.setdefault(normalized, normalized)
    return index


SKILL_ALIAS_INDEX = _skill_alias_index()


def _canonical_skill_key(skill_name: Any) -> str:
    normalized = _normalize_text(skill_name)
    return SKILL_ALIAS_INDEX.get(normalized, normalized)


def _coerce_skill_level(value: Any) -> int | None:
    try:
        level = int(value)
    except (TypeError, ValueError):
        return None
    return level if 0 <= level <= 5 else None


def _normalize_skill_profile(
    value: Any,
) -> tuple[dict[str, dict[str, Any]], list[str], list[str]]:
    """
    Normalize skill input.

    Returns a mapping by canonical skill key, validation errors, and skills whose
    level was assumed to be 2 because the user only supplied a name.
    """
    entries: list[tuple[Any, Any]] = []
    if isinstance(value, dict):
        entries = list(value.items())
    elif isinstance(value, str):
        for raw_item in _normalize_items(value):
            match = re.match(r"^(.*?)(?:\s*[:=]\s*([0-5]))?$", raw_item)
            if match:
                entries.append((match.group(1), match.group(2)))
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            if isinstance(item, dict):
                name = item.get("name") or item.get("skill")
                entries.append((name, item.get("level")))
            else:
                entries.append((item, None))

    profile: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    assumed_levels: list[str] = []
    for raw_name, raw_level in entries:
        display_name = str(raw_name or "").strip()
        if not display_name:
            errors.append("Tên kỹ năng không được để trống.")
            continue
        level = 2 if raw_level in (None, "") else _coerce_skill_level(raw_level)
        if level is None:
            errors.append(
                f"Mức kỹ năng '{display_name}' phải là số nguyên từ 0 đến 5."
            )
            continue
        if raw_level in (None, ""):
            assumed_levels.append(display_name)
        profile[_canonical_skill_key(display_name)] = {
            "name": display_name,
            "level": level,
        }
    return profile, errors, assumed_levels


def _career_skill_map(career: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        _canonical_skill_key(skill["name"]): skill
        for skill in career["required_skills"]
    }


def _skill_fit(
    career: dict[str, Any],
    skill_profile: dict[str, dict[str, Any]],
) -> tuple[int, list[str], list[dict[str, Any]]]:
    weighted_score = 0.0
    total_weight = 0.0
    matched: list[str] = []
    gaps: list[dict[str, Any]] = []

    for required_skill in career["required_skills"]:
        skill_key = _canonical_skill_key(required_skill["name"])
        current_level = skill_profile.get(skill_key, {}).get("level", 0)
        required_level = required_skill["required_level"]
        importance = required_skill["importance"]
        total_weight += importance
        weighted_score += min(current_level / required_level, 1.0) * importance
        if current_level >= required_level:
            matched.append(required_skill["name"])
        elif current_level > 0:
            matched.append(f"{required_skill['name']} (đang phát triển)")
        if current_level < required_level:
            gaps.append(
                {
                    "skill": required_skill["name"],
                    "current_level": current_level,
                    "required_level": required_level,
                    "gap": required_level - current_level,
                    "importance": importance,
                }
            )

    gaps.sort(key=lambda item: (-item["importance"], -item["gap"], item["skill"]))
    score = round(weighted_score / total_weight * 100) if total_weight else 0
    return score, matched, gaps


def _keyword_fit(
    submitted: Any,
    keywords: list[str],
) -> tuple[int, list[str]]:
    submitted_text = " ".join(
        _normalize_text(item) for item in _normalize_items(submitted)
    )
    if not submitted_text:
        return 0, []
    matches = [
        keyword
        for keyword in keywords
        if _normalize_text(keyword) in submitted_text
    ]
    return min(100, len(matches) * 50), matches


def _riasec_codes(profile: Any) -> list[str]:
    if not profile:
        return []
    if isinstance(profile, str):
        stripped = profile.strip()
        if stripped.startswith(("{", "[")):
            try:
                return _riasec_codes(json.loads(stripped))
            except json.JSONDecodeError:
                pass
        compact = re.sub(r"[^A-Z]", "", stripped.upper())
        if (
            compact
            and len(compact) <= len(RIASEC_DIMENSIONS)
            and set(compact) <= set(RIASEC_DIMENSIONS)
        ):
            return list(dict.fromkeys(compact))
        named_codes = []
        normalized_profile = _normalize_text(stripped)
        for code, details in RIASEC_DIMENSIONS.items():
            names = {
                _normalize_text(details["name"]),
                _normalize_text(details["label"]),
            }
            if any(name in normalized_profile for name in names):
                named_codes.append(code)
        if named_codes:
            return named_codes
    if isinstance(profile, dict):
        for wrapper_key in ("data", "result"):
            if wrapper_key in profile:
                nested_codes = _riasec_codes(profile[wrapper_key])
                if nested_codes:
                    return nested_codes
        if profile.get("profile_code"):
            return _riasec_codes(profile["profile_code"])
        if isinstance(profile.get("top_dimensions"), list):
            codes = [
                str(item.get("code", "")).strip().upper()
                for item in profile["top_dimensions"]
                if isinstance(item, dict)
            ]
            valid_codes = [
                code for code in codes if code in RIASEC_DIMENSIONS
            ]
            if valid_codes:
                return list(dict.fromkeys(valid_codes))
        nested_scores = profile.get("scores")
        if isinstance(nested_scores, dict):
            profile = nested_scores
        if isinstance(profile, dict):
            ranked: list[tuple[str, float]] = []
            for raw_code, raw_score in profile.items():
                normalized = str(raw_code).strip().upper()
                code = normalized[:1]
                if code not in RIASEC_DIMENSIONS:
                    for candidate, details in RIASEC_DIMENSIONS.items():
                        if _normalize_text(raw_code) in {
                            _normalize_text(details["name"]),
                            _normalize_text(details["label"]),
                        }:
                            code = candidate
                            break
                if code in RIASEC_DIMENSIONS:
                    try:
                        ranked.append((code, float(raw_score)))
                    except (TypeError, ValueError):
                        continue
            return [
                code
                for code, _ in sorted(
                    ranked,
                    key=lambda item: (-item[1], item[0]),
                )
            ]

    codes = []
    for item in _normalize_items(profile):
        candidate = str(item).strip().upper()[:1]
        if candidate in RIASEC_DIMENSIONS and candidate not in codes:
            codes.append(candidate)
    return codes


def _riasec_fit(career: dict[str, Any], profile: Any) -> tuple[int, list[str]]:
    submitted_codes = _riasec_codes(profile)
    if not submitted_codes:
        return 0, []
    weights = [1.0, 0.75, 0.5, 0.35, 0.2, 0.1]
    score = 0.0
    matches = []
    for index, code in enumerate(submitted_codes):
        if code in career["riasec"]:
            score += weights[min(index, len(weights) - 1)]
            matches.append(code)
    maximum = sum(weights[: min(len(career["riasec"]), len(weights))])
    return round(min(1.0, score / maximum) * 100), matches


def _career_fit(
    career: dict[str, Any],
    *,
    interests: Any,
    skill_profile: dict[str, dict[str, Any]],
    goals: Any,
    riasec_profile: Any,
    work_preferences: Any,
) -> dict[str, Any]:
    dimensions: dict[str, int] = {}
    evidence: dict[str, Any] = {}

    if _normalize_items(interests):
        score, matches = _keyword_fit(interests, career["interest_keywords"])
        dimensions["interests"] = score
        evidence["matched_interests"] = matches

    matched_skills: list[str] = []
    skill_gaps: list[dict[str, Any]] = []
    if skill_profile:
        score, matched_skills, skill_gaps = _skill_fit(career, skill_profile)
        dimensions["skills"] = score
        evidence["matched_skills"] = matched_skills

    if _normalize_items(goals):
        score, matches = _keyword_fit(goals, career["goal_keywords"])
        dimensions["goals"] = score
        evidence["matched_goals"] = matches

    if _riasec_codes(riasec_profile):
        score, matches = _riasec_fit(career, riasec_profile)
        dimensions["riasec"] = score
        evidence["matched_riasec"] = matches

    if _normalize_items(work_preferences):
        score, matches = _keyword_fit(
            work_preferences,
            career["work_preferences"],
        )
        dimensions["work_preferences"] = score
        evidence["matched_work_preferences"] = matches

    dimension_weights = {
        "interests": 0.30,
        "skills": 0.30,
        "goals": 0.20,
        "riasec": 0.15,
        "work_preferences": 0.05,
    }
    active_weight = sum(dimension_weights[name] for name in dimensions)
    overall = (
        round(
            sum(
                dimensions[name] * dimension_weights[name]
                for name in dimensions
            )
            / active_weight
        )
        if active_weight
        else 0
    )
    return {
        "overall_match": overall,
        "dimension_scores": dimensions,
        "evidence": evidence,
        "priority_skill_gaps": skill_gaps[:3],
    }


def search_careers(query: str, limit: int = 5) -> str:
    """
    Find careers in the local catalog by title, alias, interest, or goal keyword.

    Args:
        query: Free-text career name or keyword.
        limit: Maximum number of matches, from 1 to 10.
    Returns:
        JSON string containing ranked career summaries and matching evidence.
    Error semantics:
        Returns ``INVALID_INPUT`` for an empty query or invalid limit.
    Side effects:
        None; reads local demo data only.
    """
    normalized_query = _normalize_text(query)
    if not normalized_query:
        return _error("INVALID_INPUT", "Cần cung cấp tên nghề hoặc từ khóa.")
    try:
        result_limit = int(limit)
    except (TypeError, ValueError):
        return _error("INVALID_INPUT", "limit phải là số nguyên từ 1 đến 10.")
    if not 1 <= result_limit <= 10:
        return _error("INVALID_INPUT", "limit phải nằm trong khoảng 1 đến 10.")

    query_tokens = set(normalized_query.split())
    matches = []
    for career_id, career in CAREER_CATALOG.items():
        names = [
            _normalize_text(career_id),
            _normalize_text(career["display_name"]),
            *(_normalize_text(alias) for alias in career["aliases"]),
        ]
        search_text = _career_search_text(career_id, career)
        search_tokens = set(search_text.split())
        if normalized_query in names:
            score = 100
        elif any(normalized_query in name or name in normalized_query for name in names):
            score = 90
        else:
            overlap = len(query_tokens & search_tokens)
            score = round(overlap / len(query_tokens) * 80) if query_tokens else 0
        if score <= 0:
            continue
        matches.append(
            {
                "career_id": career_id,
                "role": career["display_name"],
                "description": career["description"],
                "riasec": career["riasec"],
                "top_skills": [
                    skill["name"]
                    for skill in sorted(
                        career["required_skills"],
                        key=lambda item: -item["importance"],
                    )[:3]
                ],
                "search_score": score,
            }
        )

    matches.sort(key=lambda item: (-item["search_score"], item["role"]))
    warnings = [] if matches else ["Không có nghề nào khớp trong catalog demo."]
    return _response(
        {
            "query": query,
            "matches": matches[:result_limit],
            "supported_career_count": len(CAREER_CATALOG),
        },
        warnings=warnings,
        confidence=0.9 if matches else 0.2,
    )


def recommend_career_paths(
    interests: list[str] | str,
    current_skills: Any,
    goals: str,
    riasec_profile: Any = None,
    work_preferences: list[str] | str | None = None,
    top_k: int = 3,
) -> str:
    """
    Rank career paths using interests, skills, goals, RIASEC, and work preferences.

    Args:
        interests: Interest phrases as a list or comma-separated string.
        current_skills: Skill names, ``{skill: level}``, or skill objects. Levels
            use a 0-5 scale; name-only skills default to level 2.
        goals: Career goals or desired work outcomes.
        riasec_profile: Optional RIASEC code, score mapping, or assessment output.
        work_preferences: Optional preferred work environments or styles.
        top_k: Number of recommendations, from 1 to 5.
    Returns:
        JSON string with ranked careers, dimension scores, evidence, skill gaps,
        confidence metadata, and limitations.
    Error semantics:
        Returns structured errors for empty profiles or invalid skill levels.
    Safety:
        Results are exploratory guidance, not a hiring or psychological decision.
    """
    skill_profile, skill_errors, assumed_levels = _normalize_skill_profile(
        current_skills
    )
    if skill_errors:
        return _error(
            "INVALID_SKILL_LEVEL",
            "Một hoặc nhiều mức kỹ năng không hợp lệ.",
            details={"errors": skill_errors},
        )
    try:
        result_count = int(top_k)
    except (TypeError, ValueError):
        return _error("INVALID_INPUT", "top_k phải là số nguyên từ 1 đến 5.")
    if not 1 <= result_count <= 5:
        return _error("INVALID_INPUT", "top_k phải nằm trong khoảng 1 đến 5.")

    has_profile = any(
        [
            _normalize_items(interests),
            skill_profile,
            _normalize_items(goals),
            _riasec_codes(riasec_profile),
            _normalize_items(work_preferences),
        ]
    )
    if not has_profile:
        return _error(
            "INSUFFICIENT_PROFILE",
            (
                "Cần ít nhất một thông tin về sở thích, kỹ năng, mục tiêu, "
                "RIASEC hoặc môi trường làm việc."
            ),
        )

    recommendations = []
    active_dimensions = 0
    for career_id, career in CAREER_CATALOG.items():
        fit = _career_fit(
            career,
            interests=interests,
            skill_profile=skill_profile,
            goals=goals,
            riasec_profile=riasec_profile,
            work_preferences=work_preferences,
        )
        active_dimensions = max(
            active_dimensions,
            len(fit["dimension_scores"]),
        )
        recommendations.append(
            {
                "career_id": career_id,
                "role": career["display_name"],
                "description": career["description"],
                "riasec": career["riasec"],
                **fit,
            }
        )

    recommendations.sort(
        key=lambda item: (-item["overall_match"], item["role"])
    )
    warnings = [
        "Kết quả chỉ dựa trên dữ liệu demo cục bộ và không phản ánh thị trường lao động."
    ]
    if assumed_levels:
        warnings.append(
            "Các kỹ năng không có mức độ được tạm giả định ở mức 2/5: "
            + ", ".join(assumed_levels)
            + "."
        )
    if active_dimensions < 2:
        warnings.append(
            "Nên cung cấp ít nhất hai nhóm thông tin để tăng độ tin cậy."
        )
    confidence = min(0.95, 0.45 + active_dimensions * 0.1)
    return _response(
        {
            "recommendations": recommendations[:result_count],
            "evaluated_careers": len(CAREER_CATALOG),
            "active_profile_dimensions": active_dimensions,
        },
        warnings=warnings,
        confidence=confidence,
    )


def get_career_requirements(target_role: str) -> str:
    """
    Return a structured local profile for a target career.

    Args:
        target_role: Career ID, display name, or supported alias.
    Returns:
        JSON string with description, RIASEC dimensions, skills and required
        levels, tasks, education paths, and related roles.
    Error semantics:
        Returns ``CAREER_NOT_FOUND`` with supported careers when resolution fails.
    Side effects:
        None; reads local demo data only.
    """
    result = _find_career(target_role)
    if result is None:
        return _error(
            "CAREER_NOT_FOUND",
            f"Không tìm thấy nghề '{target_role}' trong catalog demo.",
            details={
                "supported_roles": [
                    career["display_name"]
                    for career in CAREER_CATALOG.values()
                ]
            },
        )

    career_id, career = result
    return _response(
        {
            "career_id": career_id,
            "role": career["display_name"],
            "aliases": career["aliases"],
            "description": career["description"],
            "riasec": career["riasec"],
            "required_skills": career["required_skills"],
            "common_tasks": career["common_tasks"],
            "work_preferences": career["work_preferences"],
            "education_paths": career["education_paths"],
            "related_roles": career["related_roles"],
        },
        confidence=0.95,
    )


def analyze_skill_gap(
    target_role: str,
    current_skills: Any,
) -> str:
    """
    Compare a structured skill profile with target-career requirements.

    Args:
        target_role: Career ID, display name, or supported alias.
        current_skills: Skill names, ``{skill: level}``, or skill objects using
            levels from 0 to 5. Name-only skills default to level 2.
    Returns:
        JSON string with readiness, coverage, per-skill gaps, priorities, current
        strengths, and extra transferable skills.
    Error semantics:
        Returns structured errors for unknown careers, empty profiles, or invalid
        skill levels.
    Safety:
        Readiness measures catalog coverage only and is not a hiring assessment.
    """
    result = _find_career(target_role)
    if result is None:
        return _error(
            "CAREER_NOT_FOUND",
            f"Không tìm thấy nghề '{target_role}' trong catalog demo.",
        )

    skill_profile, errors, assumed_levels = _normalize_skill_profile(
        current_skills
    )
    if errors:
        return _error(
            "INVALID_SKILL_LEVEL",
            "Một hoặc nhiều mức kỹ năng không hợp lệ.",
            details={"errors": errors},
        )
    if not skill_profile:
        return _error(
            "INSUFFICIENT_PROFILE",
            "Cần cung cấp ít nhất một kỹ năng hiện tại.",
        )

    career_id, career = result
    readiness_score, matched, gaps = _skill_fit(career, skill_profile)
    required_map = _career_skill_map(career)
    covered_count = sum(
        1
        for skill_key in required_map
        if skill_profile.get(skill_key, {}).get("level", 0) > 0
    )
    coverage_score = round(covered_count / len(required_map) * 100)

    analysis = []
    for required_skill in career["required_skills"]:
        skill_key = _canonical_skill_key(required_skill["name"])
        current_level = skill_profile.get(skill_key, {}).get("level", 0)
        gap = max(0, required_skill["required_level"] - current_level)
        if gap == 0:
            status = "ready"
            priority = "maintain"
        elif current_level > 0:
            status = "developing"
            priority = (
                "high"
                if required_skill["importance"] >= 4 and gap >= 2
                else "medium"
            )
        else:
            status = "missing"
            priority = (
                "high" if required_skill["importance"] >= 4 else "medium"
            )
        analysis.append(
            {
                "skill": required_skill["name"],
                "category": required_skill["category"],
                "current_level": current_level,
                "required_level": required_skill["required_level"],
                "gap": gap,
                "importance": required_skill["importance"],
                "status": status,
                "priority": priority,
            }
        )

    extra_skills = [
        details["name"]
        for skill_key, details in skill_profile.items()
        if skill_key not in required_map
    ]
    warnings = [
        "Điểm sẵn sàng chỉ phản ánh yêu cầu trong catalog demo."
    ]
    if assumed_levels:
        warnings.append(
            "Các kỹ năng không có mức độ được tạm giả định ở mức 2/5: "
            + ", ".join(assumed_levels)
            + "."
        )
    return _response(
        {
            "career_id": career_id,
            "role": career["display_name"],
            "readiness_score": readiness_score,
            "coverage_score": coverage_score,
            "matched_skills": matched,
            "priority_gaps": gaps,
            "skill_analysis": analysis,
            "extra_declared_skills": extra_skills,
        },
        warnings=warnings,
        confidence=0.8 if assumed_levels else 0.9,
    )


def build_learning_roadmap(
    target_role: str,
    missing_skills: list[str] | str | dict[str, Any],
    weekly_hours: int,
    duration_weeks: int = 8,
) -> str:
    """
    Build a deterministic learning roadmap from skill gaps and time constraints.

    Args:
        target_role: Career ID, display name, or supported alias.
        missing_skills: Missing skill names or a skill-gap mapping.
        weekly_hours: Available study hours per week, from 1 to 40.
        duration_weeks: Roadmap duration in weeks, from 1 to 52.
    Returns:
        JSON string with feasibility, weekly focus, activities, deliverables, and
        milestones.
    Error semantics:
        Returns structured errors for invalid career, skills, or time constraints.
    Side effects:
        None; the roadmap is generated from local rules and is not persisted.
    """
    result = _find_career(target_role)
    if result is None:
        return _error(
            "CAREER_NOT_FOUND",
            f"Không tìm thấy nghề '{target_role}' trong catalog demo.",
        )

    skill_items = _extract_gap_skill_names(missing_skills)
    if not skill_items:
        return _error(
            "INVALID_INPUT",
            "Cần ít nhất một kỹ năng còn thiếu để tạo lộ trình.",
        )
    try:
        hours = int(weekly_hours)
        weeks = int(duration_weeks)
    except (TypeError, ValueError):
        return _error(
            "INVALID_TIME_CONSTRAINT",
            "weekly_hours và duration_weeks phải là số nguyên.",
        )
    if not 1 <= hours <= 40:
        return _error(
            "INVALID_TIME_CONSTRAINT",
            "weekly_hours phải nằm trong khoảng 1 đến 40.",
        )
    if not 1 <= weeks <= 52:
        return _error(
            "INVALID_TIME_CONSTRAINT",
            "duration_weeks phải nằm trong khoảng 1 đến 52.",
        )

    career_id, career = result
    required_map = _career_skill_map(career)
    requested_keys = list(
        dict.fromkeys(_canonical_skill_key(skill) for skill in skill_items)
    )
    planned_skills = []
    for skill_key in requested_keys:
        if skill_key in required_map:
            planned_skills.append(dict(required_map[skill_key]))
        else:
            display_name = next(
                (
                    skill
                    for skill in skill_items
                    if _canonical_skill_key(skill) == skill_key
                ),
                skill_key,
            )
            planned_skills.append(
                {
                    "name": display_name,
                    "category": "unspecified",
                    "required_level": 2,
                    "importance": 2,
                }
            )

    career_order = {
        _canonical_skill_key(skill["name"]): index
        for index, skill in enumerate(career["required_skills"])
    }
    planned_skills.sort(
        key=lambda skill: (
            career_order.get(_canonical_skill_key(skill["name"]), 999),
            -skill["importance"],
        )
    )

    estimated_hours = sum(
        skill["importance"] * skill["required_level"] * 2
        for skill in planned_skills
    )
    available_hours = hours * weeks
    feasibility_status = (
        "achievable"
        if available_hours >= estimated_hours
        else "challenging"
    )

    roadmap = []
    skill_count = len(planned_skills)
    for week in range(1, weeks + 1):
        start = (week - 1) * skill_count // weeks
        end = max(start + 1, week * skill_count // weeks)
        focus_skills = planned_skills[start:min(end, skill_count)]
        if not focus_skills:
            focus_index = min(
                (week - 1) * skill_count // weeks,
                skill_count - 1,
            )
            focus_skills = [planned_skills[focus_index]]

        progress = week / weeks
        if progress <= 0.34:
            stage = "foundation"
            activity = "Học khái niệm nền tảng và làm bài tập có hướng dẫn."
        elif progress <= 0.75:
            stage = "practice"
            activity = "Thực hành bài toán nhỏ và tự kiểm tra kết quả."
        else:
            stage = "application"
            activity = "Ứng dụng vào một phần của dự án portfolio."

        focus_names = [skill["name"] for skill in focus_skills]
        roadmap.append(
            {
                "week": week,
                "stage": stage,
                "focus_skills": focus_names,
                "study_hours": hours,
                "activities": [activity],
                "deliverable": (
                    "Hoàn thành một sản phẩm minh chứng về "
                    + ", ".join(focus_names)
                    + "."
                ),
                "completion_criteria": (
                    "Giải thích được kiến thức chính và hoàn thành bài thực hành "
                    "mà không phụ thuộc hoàn toàn vào hướng dẫn."
                ),
            }
        )

    milestone_weeks = sorted(
        {
            max(1, round(weeks * 0.25)),
            max(1, round(weeks * 0.5)),
            max(1, round(weeks * 0.75)),
            weeks,
        }
    )
    milestones = [
        {
            "week": milestone_week,
            "goal": (
                "Đánh giá tiến độ, cập nhật skill gap và điều chỉnh kế hoạch "
                "cho giai đoạn tiếp theo."
                if milestone_week < weeks
                else "Hoàn thiện dự án portfolio và tự đánh giá toàn bộ lộ trình."
            ),
        }
        for milestone_week in milestone_weeks
    ]
    warnings = [
        "Lộ trình không bao gồm khóa học hoặc dữ liệu thị trường bên ngoài."
    ]
    if feasibility_status == "challenging":
        warnings.append(
            "Quỹ thời gian thấp hơn ước lượng demo; nên tăng thời gian hoặc giảm phạm vi."
        )
    return _response(
        {
            "career_id": career_id,
            "role": career["display_name"],
            "constraints": {
                "duration_weeks": weeks,
                "weekly_hours": hours,
                "available_hours": available_hours,
            },
            "feasibility": {
                "status": feasibility_status,
                "estimated_hours": estimated_hours,
            },
            "planned_skills": [
                skill["name"] for skill in planned_skills
            ],
            "roadmap": roadmap,
            "milestones": milestones,
        },
        warnings=warnings,
        confidence=0.75,
    )


def compare_career_paths(
    career_a: str,
    career_b: str,
    current_skills: Any = (),
    interests: list[str] | str = (),
    goals: str = "",
    riasec_profile: Any = None,
) -> str:
    """
    Compare two careers using structure and optional user-profile evidence.

    Args:
        career_a: First career ID, name, or alias.
        career_b: Second career ID, name, or alias.
        current_skills: Optional structured skill profile.
        interests: Optional interests used for personal fit.
        goals: Optional career goals used for personal fit.
        riasec_profile: Optional RIASEC code or score mapping.
    Returns:
        JSON string with common and unique requirements, multi-dimensional fit,
        trade-offs, and clarification questions.
    Error semantics:
        Returns structured errors for unknown or duplicate careers and invalid
        skill levels.
    Safety:
        Does not infer salary, demand, or market opportunities.
    """
    result_a = _find_career(career_a)
    result_b = _find_career(career_b)
    if result_a is None or result_b is None:
        missing = []
        if result_a is None:
            missing.append(str(career_a))
        if result_b is None:
            missing.append(str(career_b))
        return _error(
            "CAREER_NOT_FOUND",
            "Không tìm thấy một hoặc nhiều nghề trong catalog demo.",
            details={"unresolved_careers": missing},
        )

    career_id_a, data_a = result_a
    career_id_b, data_b = result_b
    if career_id_a == career_id_b:
        return _error(
            "DUPLICATE_CAREER",
            "Cần cung cấp hai nghề khác nhau để so sánh.",
        )

    skill_profile, errors, assumed_levels = _normalize_skill_profile(
        current_skills
    )
    if errors:
        return _error(
            "INVALID_SKILL_LEVEL",
            "Một hoặc nhiều mức kỹ năng không hợp lệ.",
            details={"errors": errors},
        )

    skills_a = _career_skill_map(data_a)
    skills_b = _career_skill_map(data_b)
    common_keys = set(skills_a) & set(skills_b)
    fit_a = _career_fit(
        data_a,
        interests=interests,
        skill_profile=skill_profile,
        goals=goals,
        riasec_profile=riasec_profile,
        work_preferences=(),
    )
    fit_b = _career_fit(
        data_b,
        interests=interests,
        skill_profile=skill_profile,
        goals=goals,
        riasec_profile=riasec_profile,
        work_preferences=(),
    )

    dimensions = []
    all_dimensions = sorted(
        set(fit_a["dimension_scores"]) | set(fit_b["dimension_scores"])
    )
    for dimension in all_dimensions:
        score_a = fit_a["dimension_scores"].get(dimension, 0)
        score_b = fit_b["dimension_scores"].get(dimension, 0)
        difference = score_a - score_b
        better_fit = (
            data_a["display_name"]
            if difference >= 5
            else data_b["display_name"]
            if difference <= -5
            else "Tương đương"
        )
        dimensions.append(
            {
                "dimension": dimension,
                "career_a_score": score_a,
                "career_b_score": score_b,
                "better_fit": better_fit,
            }
        )

    difference = fit_a["overall_match"] - fit_b["overall_match"]
    recommended_choice = None
    if all_dimensions and abs(difference) >= 5:
        recommended_choice = (
            data_a["display_name"]
            if difference > 0
            else data_b["display_name"]
        )

    questions_to_clarify = []
    if not interests:
        questions_to_clarify.append("Bạn hứng thú với loại hoạt động nào?")
    if not skill_profile:
        questions_to_clarify.append(
            "Bạn đang có những kỹ năng nào và ở mức độ bao nhiêu?"
        )
    if not goals:
        questions_to_clarify.append(
            "Mục tiêu nghề nghiệp trong 1-3 năm tới của bạn là gì?"
        )
    if not _riasec_codes(riasec_profile):
        questions_to_clarify.append(
            "Bạn có muốn làm khảo sát sở thích nghề nghiệp RIASEC không?"
        )

    def career_comparison(
        career_id: str,
        career: dict[str, Any],
        career_skills: dict[str, dict[str, Any]],
        fit: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "career_id": career_id,
            "role": career["display_name"],
            "description": career["description"],
            "riasec": career["riasec"],
            "common_tasks": career["common_tasks"],
            "unique_required_skills": [
                skill["name"]
                for key, skill in career_skills.items()
                if key not in common_keys
            ],
            "overall_match": fit["overall_match"]
            if all_dimensions
            else None,
            "dimension_scores": fit["dimension_scores"],
            "priority_skill_gaps": fit["priority_skill_gaps"],
        }

    warnings = [
        "So sánh dùng dữ liệu demo và không bao gồm lương hoặc nhu cầu tuyển dụng."
    ]
    if assumed_levels:
        warnings.append(
            "Các kỹ năng không có mức độ được tạm giả định ở mức 2/5: "
            + ", ".join(assumed_levels)
            + "."
        )
    return _response(
        {
            "common_required_skills": sorted(
                (skills_a[key]["name"] for key in common_keys),
                key=_normalize_text,
            ),
            "careers": [
                career_comparison(
                    career_id_a,
                    data_a,
                    skills_a,
                    fit_a,
                ),
                career_comparison(
                    career_id_b,
                    data_b,
                    skills_b,
                    fit_b,
                ),
            ],
            "comparison_dimensions": dimensions,
            "recommended_choice": recommended_choice,
            "questions_to_clarify": questions_to_clarify,
        },
        warnings=warnings,
        confidence=0.85 if len(all_dimensions) >= 2 else 0.6,
    )


def _public_questions(
    questions: tuple[dict[str, str], ...] | list[dict[str, str]],
) -> list[dict[str, Any]]:
    return [
        {
            "question_id": question["question_id"],
            "text": question["text"],
            "required": True,
        }
        for question in questions
    ]


def _parse_assessment_answers(
    answers: Any,
) -> tuple[dict[str, int], list[str]]:
    if isinstance(answers, str):
        try:
            answers = json.loads(answers)
        except json.JSONDecodeError:
            return {}, ["answers phải là JSON object hoặc danh sách có cấu trúc."]

    raw_entries: list[tuple[Any, Any]] = []
    if isinstance(answers, dict):
        raw_entries = list(answers.items())
    elif isinstance(answers, (list, tuple)):
        if all(isinstance(item, (int, float)) for item in answers):
            question_ids = [
                question["question_id"] for question in RIASEC_QUESTION_BANK
            ]
            raw_entries = list(zip(question_ids, answers))
        else:
            for item in answers:
                if not isinstance(item, dict):
                    return {}, [
                        "Mỗi câu trả lời phải có question_id và score."
                    ]
                raw_entries.append(
                    (
                        item.get("question_id"),
                        item.get("score", item.get("answer")),
                    )
                )
    else:
        return {}, ["answers phải là object hoặc danh sách."]

    valid_ids = {
        question["question_id"] for question in RIASEC_QUESTION_BANK
    }
    parsed: dict[str, int] = {}
    errors: list[str] = []
    for raw_id, raw_score in raw_entries:
        question_id = str(raw_id or "").strip().upper()
        if question_id not in valid_ids:
            errors.append(f"Question ID không hợp lệ: '{raw_id}'.")
            continue
        try:
            score = int(raw_score)
        except (TypeError, ValueError):
            errors.append(f"Điểm của {question_id} phải là số nguyên từ 1 đến 5.")
            continue
        if not 1 <= score <= 5:
            errors.append(f"Điểm của {question_id} phải nằm trong khoảng 1 đến 5.")
            continue
        parsed[question_id] = score
    return parsed, errors


def _assessment_result(answers: dict[str, int]) -> dict[str, Any]:
    raw_scores = {code: 0 for code in RIASEC_DIMENSIONS}
    question_count = {code: 0 for code in RIASEC_DIMENSIONS}
    for question in RIASEC_QUESTION_BANK:
        code = question["dimension"]
        raw_scores[code] += answers[question["question_id"]]
        question_count[code] += 1

    normalized_scores = {}
    for code, raw_score in raw_scores.items():
        minimum = question_count[code]
        maximum = question_count[code] * 5
        normalized_scores[code] = round(
            (raw_score - minimum) / (maximum - minimum) * 100
        )

    ranked_codes = sorted(
        normalized_scores,
        key=lambda code: (-normalized_scores[code], code),
    )
    top_dimensions = [
        {
            "code": code,
            **RIASEC_DIMENSIONS[code],
            "score": normalized_scores[code],
        }
        for code in ranked_codes[:3]
    ]
    spread = normalized_scores[ranked_codes[0]] - normalized_scores[ranked_codes[-1]]
    confidence = min(0.95, 0.65 + spread / 200)
    warnings = []
    if (
        normalized_scores[ranked_codes[0]]
        - normalized_scores[ranked_codes[1]]
        <= 5
    ):
        warnings.append(
            "Hai nhóm dẫn đầu có điểm gần nhau; nên xem đây là hồ sơ kết hợp."
        )
    return {
        "assessment_type": "RIASEC",
        "assessment_version": ASSESSMENT_VERSION,
        "raw_scores": raw_scores,
        "scores": normalized_scores,
        "profile_code": "".join(ranked_codes[:3]),
        "top_dimensions": top_dimensions,
        "confidence": round(confidence, 2),
        "warnings": warnings,
        "disclaimer": (
            "Đây là khảo sát khám phá sở thích nghề nghiệp dùng dữ liệu demo, "
            "không phải chẩn đoán tâm lý."
        ),
    }


def start_career_interest_assessment(batch_size: int = 6) -> str:
    """
    Start the offline RIASEC career-interest assessment.

    Args:
        batch_size: Number of questions in the first batch, from 3 to 9.
    Returns:
        JSON string with answer scale, progress, and the first question batch.
    Error semantics:
        Returns ``INVALID_INPUT`` when batch size is outside the supported range.
    Side effects:
        None. The caller must keep cumulative answers between Agent turns.
    Safety:
        The question bank is exploratory and is not a clinical personality test.
    """
    try:
        size = int(batch_size)
    except (TypeError, ValueError):
        return _error("INVALID_INPUT", "batch_size phải là số nguyên từ 3 đến 9.")
    if not 3 <= size <= 9:
        return _error("INVALID_INPUT", "batch_size phải nằm trong khoảng 3 đến 9.")

    return _response(
        {
            "assessment_type": "RIASEC",
            "assessment_version": ASSESSMENT_VERSION,
            "state_mode": "stateless",
            "instructions": (
                "Đánh giá mỗi phát biểu từ 1 đến 5 theo mức độ phù hợp với bạn."
            ),
            "answer_scale": {
                "min": 1,
                "max": 5,
                "labels": {
                    "1": "Hoàn toàn không phù hợp",
                    "2": "Ít phù hợp",
                    "3": "Phân vân hoặc trung lập",
                    "4": "Khá phù hợp",
                    "5": "Rất phù hợp",
                },
            },
            "progress": {
                "answered": 0,
                "total": len(RIASEC_QUESTION_BANK),
                "percentage": 0,
            },
            "questions": _public_questions(RIASEC_QUESTION_BANK[:size]),
        },
        source="local_riasec_question_bank",
        confidence=0.8,
        warnings=[
            "Ứng dụng cần gửi lại toàn bộ câu trả lời đã thu thập ở mỗi lần submit."
        ],
    )


def submit_career_interest_answers(
    answers: Any,
    batch_size: int = 6,
) -> str:
    """
    Validate cumulative RIASEC answers and return the next Agent action.

    Args:
        answers: Cumulative ``{question_id: score}`` mapping or answer objects.
        batch_size: Number of unanswered questions to return, from 3 to 9.
    Returns:
        ``in_progress`` with progress and next questions, or ``success`` with the
        completed assessment result.
    Error semantics:
        Returns structured errors for malformed, unknown, or out-of-range answers.
    Side effects:
        None. This demo is stateless and does not persist assessment sessions.
    """
    try:
        size = int(batch_size)
    except (TypeError, ValueError):
        return _error("INVALID_INPUT", "batch_size phải là số nguyên từ 3 đến 9.")
    if not 3 <= size <= 9:
        return _error("INVALID_INPUT", "batch_size phải nằm trong khoảng 3 đến 9.")

    parsed, errors = _parse_assessment_answers(answers)
    if errors:
        return _error(
            "INVALID_ANSWER",
            "Một hoặc nhiều câu trả lời không hợp lệ.",
            details={"errors": errors},
        )
    if not parsed:
        return _error(
            "ASSESSMENT_INCOMPLETE",
            "Chưa có câu trả lời nào được ghi nhận.",
        )

    unanswered = [
        question
        for question in RIASEC_QUESTION_BANK
        if question["question_id"] not in parsed
    ]
    answered_count = len(parsed)
    total = len(RIASEC_QUESTION_BANK)
    progress = {
        "answered": answered_count,
        "remaining": len(unanswered),
        "total": total,
        "percentage": round(answered_count / total * 100),
    }
    if unanswered:
        return _response(
            {
                "assessment_type": "RIASEC",
                "assessment_version": ASSESSMENT_VERSION,
                "assessment_status": "in_progress",
                "progress": progress,
                "next_questions": _public_questions(unanswered[:size]),
            },
            status="in_progress",
            source="local_riasec_question_bank",
            confidence=0.8,
            warnings=[
                "Tiếp tục gửi cumulative answers, bao gồm cả các câu đã trả lời."
            ],
        )

    result = _assessment_result(parsed)
    result_warnings = result.pop("warnings")
    return _response(
        {
            "assessment_status": "completed",
            "progress": progress,
            "result": result,
        },
        source="local_riasec_scoring_rules",
        confidence=result["confidence"],
        warnings=result_warnings,
    )


def score_career_interest_assessment(answers: Any) -> str:
    """
    Score a complete set of offline RIASEC assessment answers.

    Args:
        answers: All 18 answers as a mapping, ordered score list, or answer objects.
    Returns:
        JSON string with normalized RIASEC scores, profile code, top dimensions,
        confidence, and a non-clinical disclaimer.
    Error semantics:
        Returns ``ASSESSMENT_INCOMPLETE`` with missing question IDs or
        ``INVALID_ANSWER`` for invalid input.
    Side effects:
        None; scoring is deterministic and local.
    """
    parsed, errors = _parse_assessment_answers(answers)
    if errors:
        return _error(
            "INVALID_ANSWER",
            "Một hoặc nhiều câu trả lời không hợp lệ.",
            details={"errors": errors},
        )

    missing_ids = [
        question["question_id"]
        for question in RIASEC_QUESTION_BANK
        if question["question_id"] not in parsed
    ]
    if missing_ids:
        return _error(
            "ASSESSMENT_INCOMPLETE",
            "Cần trả lời đủ câu hỏi trước khi chấm điểm.",
            details={
                "answered": len(parsed),
                "total": len(RIASEC_QUESTION_BANK),
                "missing_question_ids": missing_ids,
            },
        )

    result = _assessment_result(parsed)
    result_warnings = result.pop("warnings")
    return _response(
        result,
        source="local_riasec_scoring_rules",
        confidence=result["confidence"],
        warnings=result_warnings,
    )


# Public allowlist used by the Agent executor to validate and dispatch Actions.
AVAILABLE_TOOLS = {
    "search_careers": search_careers,
    "recommend_career_paths": recommend_career_paths,
    "get_career_requirements": get_career_requirements,
    "analyze_skill_gap": analyze_skill_gap,
    "build_learning_roadmap": build_learning_roadmap,
    "compare_career_paths": compare_career_paths,
    "start_career_interest_assessment": start_career_interest_assessment,
    "submit_career_interest_answers": submit_career_interest_answers,
    "score_career_interest_assessment": score_career_interest_assessment,
}
