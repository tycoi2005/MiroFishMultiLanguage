"""
Multilingual API response messages.
"""

_MESSAGES = {
    # graph.py
    "project_not_found": {
        "en": "Project not found: {id}",
        "zh": "项目不存在: {id}",
        "vi": "Không tìm thấy dự án: {id}",
        "de": "Projekt nicht gefunden: {id}",
    },
    "project_deleted": {
        "en": "Project deleted",
        "zh": "项目已删除",
        "vi": "Dự án đã được xóa",
        "de": "Projekt gelöscht",
    },
    "project_reset": {
        "en": "Project reset",
        "zh": "项目已重置",
        "vi": "Dự án đã được đặt lại",
        "de": "Projekt zurückgesetzt",
    },
    "provide_sim_requirement": {
        "en": "Please provide a simulation requirement description",
        "zh": "请提供模拟需求描述",
        "vi": "Vui lòng cung cấp mô tả yêu cầu mô phỏng",
        "de": "Bitte geben Sie eine Simulationsanforderungsbeschreibung an",
    },
    "upload_at_least_one": {
        "en": "Please upload at least one document file",
        "zh": "请至少上传一个文档文件",
        "vi": "Vui lòng tải lên ít nhất một tệp tài liệu",
        "de": "Bitte laden Sie mindestens eine Dokumentdatei hoch",
    },
    "no_docs_processed": {
        "en": "No documents were processed successfully. Please check file formats",
        "zh": "没有成功处理任何文档，请检查文件格式",
        "vi": "Không có tài liệu nào được xử lý thành công. Vui lòng kiểm tra định dạng tệp",
        "de": "Keine Dokumente wurden erfolgreich verarbeitet. Bitte überprüfen Sie die Dateiformate",
    },
    "graph_build_started": {
        "en": "Graph build task started",
        "zh": "图谱构建任务已启动",
        "vi": "Tác vụ xây dựng đồ thị đã bắt đầu",
        "de": "Graph-Erstellungsaufgabe gestartet",
    },
    "config_error": {
        "en": "Configuration error: {detail}",
        "zh": "配置错误: {detail}",
        "vi": "Lỗi cấu hình: {detail}",
        "de": "Konfigurationsfehler: {detail}",
    },
    "provide_project_id": {
        "en": "Please provide project_id",
        "zh": "请提供 project_id",
        "vi": "Vui lòng cung cấp project_id",
        "de": "Bitte geben Sie die project_id an",
    },
    # simulation.py
    "zep_not_configured": {
        "en": "ZEP_API_KEY is not configured",
        "zh": "ZEP_API_KEY未配置",
        "vi": "ZEP_API_KEY chưa được cấu hình",
        "de": "ZEP_API_KEY ist nicht konfiguriert",
    },
    "entity_not_found": {
        "en": "Entity not found: {id}",
        "zh": "实体不存在: {id}",
        "vi": "Không tìm thấy thực thể: {id}",
        "de": "Entität nicht gefunden: {id}",
    },
    "provide_simulation_id": {
        "en": "Please provide simulation_id",
        "zh": "请提供 simulation_id",
        "vi": "Vui lòng cung cấp simulation_id",
        "de": "Bitte geben Sie die simulation_id an",
    },
    "provide_graph_id": {
        "en": "Please provide graph_id",
        "zh": "请提供 graph_id",
        "vi": "Vui lòng cung cấp graph_id",
        "de": "Bitte geben Sie die graph_id an",
    },
    "provide_agent_id": {
        "en": "Please provide agent_id",
        "zh": "请提供 agent_id",
        "vi": "Vui lòng cung cấp agent_id",
        "de": "Bitte geben Sie die agent_id an",
    },
    "sim_not_found": {
        "en": "Simulation not found: {id}",
        "zh": "模拟不存在: {id}",
        "vi": "Không tìm thấy mô phỏng: {id}",
        "de": "Simulation nicht gefunden: {id}",
    },
    "project_no_graph": {
        "en": "Project has no graph built yet. Please call /api/graph/build first",
        "zh": "项目尚未构建图谱，请先调用 /api/graph/build",
        "vi": "Dự án chưa xây dựng đồ thị. Vui lòng gọi /api/graph/build trước",
        "de": "Projekt hat noch keinen Graph erstellt. Bitte rufen Sie zuerst /api/graph/build auf",
    },
    "already_prepared": {
        "en": "Preparation already completed, no need to regenerate",
        "zh": "已有完成的准备工作，无需重复生成",
        "vi": "Chuẩn bị đã hoàn tất, không cần tạo lại",
        "de": "Vorbereitung bereits abgeschlossen, keine Neugenerierung erforderlich",
    },
    "missing_sim_requirement": {
        "en": "Project is missing simulation requirement description",
        "zh": "项目缺少模拟需求描述",
        "vi": "Dự án thiếu mô tả yêu cầu mô phỏng",
        "de": "Projekt fehlt die Simulationsanforderungsbeschreibung",
    },
    "task_not_found": {
        "en": "Task not found: {id}",
        "zh": "任务不存在: {id}",
        "vi": "Không tìm thấy tác vụ: {id}",
        "de": "Aufgabe nicht gefunden: {id}",
    },
    "config_not_found": {
        "en": "Simulation config not found. Please call /prepare first",
        "zh": "模拟配置不存在，请先调用 /prepare 接口",
        "vi": "Không tìm thấy cấu hình mô phỏng. Vui lòng gọi /prepare trước",
        "de": "Simulationskonfiguration nicht gefunden. Bitte rufen Sie zuerst /prepare auf",
    },
    "unknown_script": {
        "en": "Unknown script: {name}",
        "zh": "未知脚本: {name}",
        "vi": "Tập lệnh không xác định: {name}",
        "de": "Unbekanntes Skript: {name}",
    },
    "no_matching_entities": {
        "en": "No matching entities found",
        "zh": "没有找到符合条件的实体",
        "vi": "Không tìm thấy thực thể phù hợp",
        "de": "Keine passenden Entitäten gefunden",
    },
    "max_rounds_positive": {
        "en": "max_rounds must be a positive integer",
        "zh": "max_rounds 必须是正整数",
        "vi": "max_rounds phải là số nguyên dương",
        "de": "max_rounds muss eine positive Ganzzahl sein",
    },
    "max_rounds_invalid": {
        "en": "max_rounds must be a valid integer",
        "zh": "max_rounds 必须是有效的整数",
        "vi": "max_rounds phải là số nguyên hợp lệ",
        "de": "max_rounds muss eine gültige Ganzzahl sein",
    },
    "invalid_platform": {
        "en": "Invalid platform type: {type}. Must be 'twitter' or 'reddit'",
        "zh": "无效的平台类型: {type}，platform 参数只能是 'twitter' 或 'reddit'",
        "vi": "Loại nền tảng không hợp lệ: {type}. Phải là 'twitter' hoặc 'reddit'",
        "de": "Ungültiger Plattformtyp: {type}. Muss 'twitter' oder 'reddit' sein",
    },
    "sim_running_stop_first": {
        "en": "Simulation is running. Please call /stop first",
        "zh": "模拟正在运行中，请先调用 /stop 接口停止",
        "vi": "Mô phỏng đang chạy. Vui lòng gọi /stop trước",
        "de": "Simulation läuft. Bitte rufen Sie zuerst /stop auf",
    },
    "sim_not_ready": {
        "en": "Simulation is not ready. Current status: {status}",
        "zh": "模拟未准备好，当前状态: {status}",
        "vi": "Mô phỏng chưa sẵn sàng. Trạng thái hiện tại: {status}",
        "de": "Simulation ist nicht bereit. Aktueller Status: {status}",
    },
    "graph_memory_needs_id": {
        "en": "Enabling graph memory updates requires a valid graph_id",
        "zh": "启用图谱记忆更新需要有效的 graph_id",
        "vi": "Bật cập nhật bộ nhớ đồ thị yêu cầu graph_id hợp lệ",
        "de": "Zum Aktivieren von Graph-Speicheraktualisierungen ist eine gültige graph_id erforderlich",
    },
    "db_not_exist": {
        "en": "Database does not exist. The simulation may not have run yet",
        "zh": "数据库不存在，模拟可能尚未运行",
        "vi": "Cơ sở dữ liệu không tồn tại. Mô phỏng có thể chưa được chạy",
        "de": "Datenbank existiert nicht. Die Simulation wurde möglicherweise noch nicht ausgeführt",
    },
    "provide_prompt": {
        "en": "Please provide prompt (interview question)",
        "zh": "请提供 prompt（采访问题）",
        "vi": "Vui lòng cung cấp prompt (câu hỏi phỏng vấn)",
        "de": "Bitte geben Sie einen Prompt (Interviewfrage) an",
    },
    "provide_interviews": {
        "en": "Please provide interviews (interview list)",
        "zh": "请提供 interviews（采访列表）",
        "vi": "Vui lòng cung cấp interviews (danh sách phỏng vấn)",
        "de": "Bitte geben Sie interviews (Interviewliste) an",
    },
    "platform_invalid": {
        "en": "platform parameter must be 'twitter' or 'reddit'",
        "zh": "platform 参数只能是 'twitter' 或 'reddit'",
        "vi": "Tham số platform phải là 'twitter' hoặc 'reddit'",
        "de": "Der Parameter platform muss 'twitter' oder 'reddit' sein",
    },
    "sim_env_not_running": {
        "en": "Simulation environment is not running or has been closed. Please ensure the simulation has completed and the environment is active",
        "zh": "模拟环境未运行或已关闭。请确保模拟已完成且环境处于活跃状态",
        "vi": "Môi trường mô phỏng không chạy hoặc đã đóng. Vui lòng đảm bảo mô phỏng đã hoàn tất và môi trường đang hoạt động",
        "de": "Simulationsumgebung läuft nicht oder wurde geschlossen. Bitte stellen Sie sicher, dass die Simulation abgeschlossen ist und die Umgebung aktiv ist",
    },
    "interview_missing_field": {
        "en": "Interview item #{idx} is missing {field}",
        "zh": "采访列表第{idx}项缺少 {field}",
        "vi": "Mục phỏng vấn #{idx} thiếu {field}",
        "de": "Interviewelement #{idx} fehlt {field}",
    },
    "env_running": {
        "en": "Environment is running and can receive Interview commands",
        "zh": "环境正在运行，可以接收Interview命令",
        "vi": "Môi trường đang chạy và có thể nhận lệnh Interview",
        "de": "Umgebung läuft und kann Interview-Befehle empfangen",
    },
    "env_close_sent": {
        "en": "Environment close command sent",
        "zh": "环境关闭命令已发送",
        "vi": "Đã gửi lệnh đóng môi trường",
        "de": "Befehl zum Schließen der Umgebung gesendet",
    },
    # report.py
    "report_task_started": {
        "en": "Report generation task started",
        "zh": "报告生成任务已启动",
        "vi": "Tác vụ tạo báo cáo đã bắt đầu",
        "de": "Berichterstellungsaufgabe gestartet",
    },
    "provide_message": {
        "en": "Please provide message",
        "zh": "请提供 message",
        "vi": "Vui lòng cung cấp message",
        "de": "Bitte geben Sie eine Nachricht an",
    },
    "report_exists": {
        "en": "Report already exists",
        "zh": "报告已存在",
        "vi": "Báo cáo đã tồn tại",
        "de": "Bericht existiert bereits",
    },
    "report_generated": {
        "en": "Report already generated",
        "zh": "报告已生成",
        "vi": "Báo cáo đã được tạo",
        "de": "Bericht bereits erstellt",
    },
    "missing_graph_id": {
        "en": "Missing graph ID",
        "zh": "缺少图谱ID",
        "vi": "Thiếu ID đồ thị",
        "de": "Graph-ID fehlt",
    },
    "missing_sim_desc": {
        "en": "Missing simulation requirement description",
        "zh": "缺少模拟需求描述",
        "vi": "Thiếu mô tả yêu cầu mô phỏng",
        "de": "Simulationsanforderungsbeschreibung fehlt",
    },
    "report_started_check_progress": {
        "en": "Report generation task started. Check progress via the status endpoint",
        "zh": "报告生成任务已启动，请通过状态接口查询进度",
        "vi": "Tác vụ tạo báo cáo đã bắt đầu. Kiểm tra tiến trình qua endpoint trạng thái",
        "de": "Berichterstellungsaufgabe gestartet. Überprüfen Sie den Fortschritt über den Status-Endpunkt",
    },
    "provide_task_or_sim_id": {
        "en": "Please provide task_id or simulation_id",
        "zh": "请提供 task_id 或 simulation_id",
        "vi": "Vui lòng cung cấp task_id hoặc simulation_id",
        "de": "Bitte geben Sie task_id oder simulation_id an",
    },
    "report_not_found": {
        "en": "Report not found",
        "zh": "报告不存在",
        "vi": "Không tìm thấy báo cáo",
        "de": "Bericht nicht gefunden",
    },
    "no_report_for_sim": {
        "en": "No report found for this simulation",
        "zh": "该模拟暂无报告",
        "vi": "Không tìm thấy báo cáo cho mô phỏng này",
        "de": "Kein Bericht für diese Simulation gefunden",
    },
    "report_deleted": {
        "en": "Report deleted",
        "zh": "报告已删除",
        "vi": "Báo cáo đã được xóa",
        "de": "Bericht gelöscht",
    },
    "report_progress_unavailable": {
        "en": "Report not found or progress info unavailable",
        "zh": "报告不存在或进度信息不可用",
        "vi": "Không tìm thấy báo cáo hoặc thông tin tiến trình không khả dụng",
        "de": "Bericht nicht gefunden oder Fortschrittsinformationen nicht verfügbar",
    },
    "section_not_found": {
        "en": "Section not found: {id}",
        "zh": "章节不存在: {id}",
        "vi": "Không tìm thấy phần: {id}",
        "de": "Abschnitt nicht gefunden: {id}",
    },
    "provide_graph_and_query": {
        "en": "Please provide graph_id and query",
        "zh": "请提供 graph_id 和 query",
        "vi": "Vui lòng cung cấp graph_id và query",
        "de": "Bitte geben Sie graph_id und query an",
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
