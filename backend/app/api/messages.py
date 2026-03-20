"""
Bilingual API response messages.
"""

_MESSAGES = {
    # graph.py
    "project_not_found": {"en": "Project not found: {id}", "zh": "项目不存在: {id}"},
    "project_deleted": {"en": "Project deleted", "zh": "项目已删除"},
    "project_reset": {"en": "Project reset", "zh": "项目已重置"},
    "provide_sim_requirement": {
        "en": "Please provide a simulation requirement description",
        "zh": "请提供模拟需求描述",
    },
    "upload_at_least_one": {
        "en": "Please upload at least one document file",
        "zh": "请至少上传一个文档文件",
    },
    "no_docs_processed": {
        "en": "No documents were processed successfully. Please check file formats",
        "zh": "没有成功处理任何文档，请检查文件格式",
    },
    "graph_build_started": {
        "en": "Graph build task started",
        "zh": "图谱构建任务已启动",
    },
    "config_error": {"en": "Configuration error: {detail}", "zh": "配置错误: {detail}"},
    "provide_project_id": {
        "en": "Please provide project_id",
        "zh": "请提供 project_id",
    },
    # simulation.py
    "zep_not_configured": {
        "en": "ZEP_API_KEY is not configured",
        "zh": "ZEP_API_KEY未配置",
    },
    "entity_not_found": {"en": "Entity not found: {id}", "zh": "实体不存在: {id}"},
    "provide_simulation_id": {
        "en": "Please provide simulation_id",
        "zh": "请提供 simulation_id",
    },
    "provide_graph_id": {"en": "Please provide graph_id", "zh": "请提供 graph_id"},
    "provide_agent_id": {"en": "Please provide agent_id", "zh": "请提供 agent_id"},
    "sim_not_found": {"en": "Simulation not found: {id}", "zh": "模拟不存在: {id}"},
    "project_no_graph": {
        "en": "Project has no graph built yet. Please call /api/graph/build first",
        "zh": "项目尚未构建图谱，请先调用 /api/graph/build",
    },
    "already_prepared": {
        "en": "Preparation already completed, no need to regenerate",
        "zh": "已有完成的准备工作，无需重复生成",
    },
    "missing_sim_requirement": {
        "en": "Project is missing simulation requirement description",
        "zh": "项目缺少模拟需求描述",
    },
    "task_not_found": {"en": "Task not found: {id}", "zh": "任务不存在: {id}"},
    "config_not_found": {
        "en": "Simulation config not found. Please call /prepare first",
        "zh": "模拟配置不存在，请先调用 /prepare 接口",
    },
    "unknown_script": {"en": "Unknown script: {name}", "zh": "未知脚本: {name}"},
    "no_matching_entities": {
        "en": "No matching entities found",
        "zh": "没有找到符合条件的实体",
    },
    "max_rounds_positive": {
        "en": "max_rounds must be a positive integer",
        "zh": "max_rounds 必须是正整数",
    },
    "max_rounds_invalid": {
        "en": "max_rounds must be a valid integer",
        "zh": "max_rounds 必须是有效的整数",
    },
    "invalid_platform": {
        "en": "Invalid platform type: {type}. Must be 'twitter' or 'reddit'",
        "zh": "无效的平台类型: {type}，platform 参数只能是 'twitter' 或 'reddit'",
    },
    "sim_running_stop_first": {
        "en": "Simulation is running. Please call /stop first",
        "zh": "模拟正在运行中，请先调用 /stop 接口停止",
    },
    "sim_not_ready": {
        "en": "Simulation is not ready. Current status: {status}",
        "zh": "模拟未准备好，当前状态: {status}",
    },
    "graph_memory_needs_id": {
        "en": "Enabling graph memory updates requires a valid graph_id",
        "zh": "启用图谱记忆更新需要有效的 graph_id",
    },
    "db_not_exist": {
        "en": "Database does not exist. The simulation may not have run yet",
        "zh": "数据库不存在，模拟可能尚未运行",
    },
    "provide_prompt": {
        "en": "Please provide prompt (interview question)",
        "zh": "请提供 prompt（采访问题）",
    },
    "provide_interviews": {
        "en": "Please provide interviews (interview list)",
        "zh": "请提供 interviews（采访列表）",
    },
    "platform_invalid": {
        "en": "platform parameter must be 'twitter' or 'reddit'",
        "zh": "platform 参数只能是 'twitter' 或 'reddit'",
    },
    "sim_env_not_running": {
        "en": "Simulation environment is not running or has been closed. Please ensure the simulation has completed and the environment is active",
        "zh": "模拟环境未运行或已关闭。请确保模拟已完成且环境处于活跃状态",
    },
    "interview_missing_field": {
        "en": "Interview item #{idx} is missing {field}",
        "zh": "采访列表第{idx}项缺少 {field}",
    },
    "env_running": {
        "en": "Environment is running and can receive Interview commands",
        "zh": "环境正在运行，可以接收Interview命令",
    },
    "env_close_sent": {
        "en": "Environment close command sent",
        "zh": "环境关闭命令已发送",
    },
    # report.py
    "report_task_started": {
        "en": "Report generation task started",
        "zh": "报告生成任务已启动",
    },
    "provide_message": {"en": "Please provide message", "zh": "请提供 message"},
    "report_exists": {"en": "Report already exists", "zh": "报告已存在"},
    "report_generated": {"en": "Report already generated", "zh": "报告已生成"},
    "missing_graph_id": {"en": "Missing graph ID", "zh": "缺少图谱ID"},
    "missing_sim_desc": {
        "en": "Missing simulation requirement description",
        "zh": "缺少模拟需求描述",
    },
    "report_started_check_progress": {
        "en": "Report generation task started. Check progress via the status endpoint",
        "zh": "报告生成任务已启动，请通过状态接口查询进度",
    },
    "provide_task_or_sim_id": {
        "en": "Please provide task_id or simulation_id",
        "zh": "请提供 task_id 或 simulation_id",
    },
    "report_not_found": {"en": "Report not found", "zh": "报告不存在"},
    "no_report_for_sim": {
        "en": "No report found for this simulation",
        "zh": "该模拟暂无报告",
    },
    "report_deleted": {"en": "Report deleted", "zh": "报告已删除"},
    "report_progress_unavailable": {
        "en": "Report not found or progress info unavailable",
        "zh": "报告不存在或进度信息不可用",
    },
    "section_not_found": {"en": "Section not found: {id}", "zh": "章节不存在: {id}"},
    "provide_graph_and_query": {
        "en": "Please provide graph_id and query",
        "zh": "请提供 graph_id 和 query",
    },
}


def msg(key: str, locale: str = "en", **kwargs) -> str:
    """Get a localized message. Falls back to English."""
    entry = _MESSAGES.get(key, {})
    text = entry.get(locale, entry.get("en", key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


def get_request_locale():
    """Extract locale from Flask request args or JSON body."""
    from flask import request

    locale = request.args.get("locale") or request.args.get("lang")
    if not locale:
        try:
            data = request.get_json(silent=True)
            if data:
                locale = data.get("locale") or data.get("lang")
        except Exception:
            pass
    return locale or "en"
