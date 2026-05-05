from langchain_core.prompts import ChatPromptTemplate


def build_rag_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "你是一个服务于打工人的智能行业情报分析师。"
                    "请基于提供的资讯上下文回答问题，优先给出核心结论、业务影响、风险提醒和建议动作。"
                    "如果上下文不足，请明确说明不知道，不要编造。"
                ),
            ),
            (
                "human",
                "问题：{question}\n\n资讯上下文：\n{context}",
            ),
        ]
    )


def build_daily_report_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "你是行业情报日报助手。请面向职场用户输出结构清晰的日报，"
                    "包含今日重点、业务影响、风险提示、建议跟进动作四部分。"
                ),
            ),
            (
                "human",
                "请基于以下资讯生成日报，输出 Markdown：\n\n{context}",
            ),
        ]
    )
