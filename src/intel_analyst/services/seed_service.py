"""Seed sample data into the vector store for testing the query flow."""
from datetime import datetime, timezone

from intel_analyst.schemas.article import ArticleRecord
from intel_analyst.services.ingestion_service import IngestionService

SAMPLE_ARTICLES = [
    {
        "title": "深圳半导体产业链协同大会即将召开",
        "content": (
            "深圳市半导体行业协会宣布将于6月召开产业链协同大会，聚焦芯片设计、先进封测与本地供应链协作。"
            "大会将邀请华为海思、中芯国际、华大半导体等50余家重点企业参与，探讨在当前国际形势下如何构建"
            "自主可控的半导体供应链体系。协会秘书长表示，深圳作为中国集成电路产业重镇，2025年产业规模"
            "突破8000亿元，增速达18%，其中芯片设计业贡献超过45%。"
        ),
        "summary": "深圳半导体行业协会宣布将于6月召开产业链协同大会，聚焦芯片设计、先进封测与本地供应链协作，释放地方资源整合信号。",
        "url": "https://example.com/news/sz-semicon-2026",
        "industry": "半导体",
        "source_name": "Shenzhen SIA",
        "published_at": datetime(2026, 5, 16, 8, 0, tzinfo=timezone.utc),
        "tags": ["产业协同", "芯片设计", "先进封测"],
    },
    {
        "title": "多家半导体设备与材料企业进入新一轮融资窗口",
        "content": (
            "2026年第二季度以来，国内半导体设备与材料企业融资活动明显加速。据协会统计，4-5月已有"
            "超过12家企业完成新一轮融资，总金额超过80亿元，涉及CMP设备、离子注入机、光刻胶、高纯"
            "试剂等关键领域。投资机构普遍认为，在国产替代大趋势下，设备材料赛道将迎来3-5年的黄金"
            "发展期。其中，两家成立于2020年后的初创企业估值已突破50亿元。"
        ),
        "summary": "多家设备与材料企业进入新一轮资本窗口，融资节奏与扩产意愿同步提升，反映市场对国产替代的强烈预期。",
        "url": "https://example.com/news/funding-wave-2026",
        "industry": "半导体",
        "source_name": "Shenzhen SIA",
        "published_at": datetime(2026, 5, 15, 10, 0, tzinfo=timezone.utc),
        "tags": ["投融资", "设备材料", "国产替代"],
    },
    {
        "title": "长三角集成电路产业联盟成立，推动区域协同创新",
        "content": (
            "上海、江苏、浙江、安徽四地集成电路行业协会日前联合成立长三角集成电路产业联盟。联盟首期"
            "将推动三个方向：共建IP共享池、联合人才培养、跨区域产能调度。数据显示，长三角地区集成电路"
            "产业产值占全国比重超过55%，联盟的成立有望进一步提升区域资源配置效率，降低重复建设。"
        ),
        "summary": "长三角四地联合成立集成电路产业联盟，推动IP共享、人才培养和产能调度协同。",
        "url": "https://example.com/news/yangtze-alliance-2026",
        "industry": "半导体",
        "source_name": "Shenzhen SIA",
        "published_at": datetime(2026, 5, 14, 14, 0, tzinfo=timezone.utc),
        "tags": ["区域协同", "产业联盟", "长三角"],
    },
    {
        "title": "AI芯片需求爆发，算力基础设施建设提速",
        "content": (
            "受大模型训练和推理需求持续拉动，2026年国内AI芯片市场预计同比增长65%，市场规模将突破"
            "3000亿元。寒武纪、地平线、壁仞科技等本土AI芯片企业纷纷推出新一代产品，性能较上一代"
            "提升2-3倍。同时，各地智算中心建设进入高峰期，年内在建算力项目超过80个，总投资规模"
            "超过2000亿元。分析人士指出，AI芯片的竞争焦点正从训练侧向推理侧转移。"
        ),
        "summary": "AI芯片需求爆发式增长，国产AI芯片企业推出新一代产品，智算中心建设进入高峰期。",
        "url": "https://example.com/news/ai-chip-boom-2026",
        "industry": "半导体",
        "source_name": "Shenzhen SIA",
        "published_at": datetime(2026, 5, 13, 9, 0, tzinfo=timezone.utc),
        "tags": ["AI芯片", "算力基建", "大模型"],
    },
    {
        "title": "第三代半导体材料量产提速，碳化硅产能翻倍",
        "content": (
            "国内碳化硅衬底产能2026年迎来爆发，天岳先进、天科合达等龙头企业产能规划合计超过300万片/年。"
            "随着6英寸产线良率突破85%，碳化硅器件成本较2024年下降约40%，加速在新能源汽车、光伏逆变器"
            "等场景的渗透。业内预计，到2027年国内碳化硅市场规模将突破500亿元，年复合增长率保持50%以上。"
        ),
        "summary": "碳化硅产能大幅提升，良率突破加速成本下降，新能源场景渗透率快速提升。",
        "url": "https://example.com/news/sic-boom-2026",
        "industry": "半导体",
        "source_name": "Shenzhen SIA",
        "published_at": datetime(2026, 5, 12, 11, 0, tzinfo=timezone.utc),
        "tags": ["碳化硅", "第三代半导体", "新能源"],
    },
]


class SeedService:
    """Populate the vector store with sample articles for testing."""

    def seed(self) -> int:
        service = IngestionService()
        articles = [self._build_article(data) for data in SAMPLE_ARTICLES]
        return service.ingest_articles(articles)

    @staticmethod
    def _build_article(data: dict) -> ArticleRecord:
        return ArticleRecord(
            source_name=data["source_name"],
            industry=data["industry"],
            url=data["url"],
            title=data["title"],
            summary=data["summary"],
            content=data["content"],
            published_at=data["published_at"],
            tags=data["tags"],
            captured_at=datetime.now(timezone.utc),
            content_hash=str(hash(data["title"])),
            extracted_tables=[],
            table_paths=[],
        )
