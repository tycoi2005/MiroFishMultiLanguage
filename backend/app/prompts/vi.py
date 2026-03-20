"""Vietnamese (vi) prompt constants for MiroFish."""

# ═══════════════════════════════════════════════════════════════
# report_agent.py — Mô tả công cụ
# ═══════════════════════════════════════════════════════════════

TOOL_DESC_INSIGHT_FORGE = """\
[Truy xuất Thông tin Chuyên sâu — Công cụ Truy xuất Mạnh mẽ]
Đây là chức năng truy xuất mạnh mẽ của chúng tôi, được xây dựng riêng cho phân tích chuyên sâu. Công cụ sẽ:
1. Tự động phân tách câu hỏi của bạn thành nhiều câu hỏi phụ
2. Truy xuất thông tin từ đồ thị mô phỏng trên nhiều chiều
3. Tổng hợp kết quả từ tìm kiếm ngữ nghĩa, phân tích thực thể và truy vết chuỗi quan hệ
4. Trả về nội dung truy xuất toàn diện và chuyên sâu nhất

[Trường hợp Sử dụng]
- Cần phân tích chuyên sâu một chủ đề
- Cần hiểu nhiều khía cạnh của một sự kiện
- Cần thu thập tài liệu phong phú để hỗ trợ một phần của báo cáo

[Nội dung Trả về]
- Các sự kiện gốc có liên quan (có thể trích dẫn trực tiếp)
- Thông tin chuyên sâu về thực thể cốt lõi
- Phân tích chuỗi quan hệ"""

TOOL_DESC_PANORAMA_SEARCH = """\
[PanoramaSearch — Xem Toàn cảnh]
Công cụ này cung cấp cái nhìn tổng quan hoàn chỉnh về kết quả mô phỏng, đặc biệt phù hợp để hiểu diễn biến sự kiện. Công cụ sẽ:
1. Truy xuất tất cả các nút và quan hệ liên quan
2. Phân biệt giữa các sự kiện hiện hành và các sự kiện lịch sử/đã hết hạn
3. Giúp bạn hiểu dư luận đã phát triển như thế nào

[Trường hợp Sử dụng]
- Cần hiểu quỹ đạo hoàn chỉnh của một sự kiện
- Cần so sánh sự thay đổi dư luận qua các giai đoạn khác nhau
- Cần thu thập thông tin toàn diện về thực thể và quan hệ

[Nội dung Trả về]
- Các sự kiện hiện hành (kết quả mô phỏng mới nhất)
- Các sự kiện lịch sử/đã hết hạn (hồ sơ diễn biến)
- Tất cả các thực thể liên quan"""

TOOL_DESC_QUICK_SEARCH = """\
[QuickSearch — Truy xuất Nhanh]
Công cụ truy xuất nhẹ, nhanh chóng, phù hợp cho các truy vấn thông tin đơn giản, trực tiếp.

[Trường hợp Sử dụng]
- Cần tra cứu nhanh một thông tin cụ thể
- Cần xác minh một sự kiện
- Truy xuất thông tin đơn giản

[Nội dung Trả về]
- Danh sách các sự kiện liên quan nhất đến truy vấn"""

TOOL_DESC_INTERVIEW_AGENTS = """\
[Phỏng vấn Chuyên sâu — Phỏng vấn Thực tế với Agent (Hai Nền tảng)]
Gọi API phỏng vấn của môi trường mô phỏng OASIS để tiến hành phỏng vấn thực tế với các Agent đang chạy trong mô phỏng!
Đây KHÔNG phải là mô phỏng bởi LLM — công cụ gọi giao diện phỏng vấn thực tế để thu thập phản hồi gốc từ các Agent mô phỏng.
Mặc định, phỏng vấn được tiến hành đồng thời trên cả Twitter và Reddit để thu thập quan điểm toàn diện hơn.

Quy trình:
1. Tự động đọc tệp hồ sơ để tìm hiểu về tất cả các Agent mô phỏng
2. Lựa chọn thông minh các Agent phù hợp nhất với chủ đề phỏng vấn (ví dụ: sinh viên, truyền thông, quan chức)
3. Tự động tạo câu hỏi phỏng vấn
4. Gọi endpoint /api/simulation/interview/batch để phỏng vấn thực tế trên hai nền tảng
5. Tổng hợp tất cả kết quả phỏng vấn và cung cấp phân tích đa góc nhìn

[Trường hợp Sử dụng]
- Cần hiểu quan điểm về sự kiện từ các vai trò khác nhau (Sinh viên nghĩ gì? Truyền thông? Quan chức?)
- Cần thu thập ý kiến và lập trường từ nhiều bên
- Cần thu thập phản hồi thực tế từ các Agent mô phỏng (từ môi trường mô phỏng OASIS)
- Muốn làm báo cáo sinh động hơn bằng cách đưa vào "bản ghi phỏng vấn"

[Nội dung Trả về]
- Thông tin danh tính của các Agent được phỏng vấn
- Phản hồi phỏng vấn của mỗi Agent trên cả Twitter và Reddit
- Trích dẫn quan trọng (có thể trích dẫn trực tiếp)
- Tóm tắt phỏng vấn và so sánh quan điểm

[Quan trọng] Môi trường mô phỏng OASIS phải đang chạy để sử dụng tính năng này!"""

# ── Prompt lập dàn ý ──

PLAN_SYSTEM_PROMPT = """\
Bạn là một chuyên gia viết "Báo cáo Dự đoán Tương lai," sở hữu "tầm nhìn toàn năng" về thế giới mô phỏng — bạn có thể quan sát mọi hành vi, phát ngôn và tương tác của từng Agent trong mô phỏng.

[Khái niệm Cốt lõi]
Chúng tôi đã xây dựng một thế giới mô phỏng và đưa vào một "yêu cầu mô phỏng" cụ thể làm biến số. Sự phát triển của thế giới mô phỏng tạo thành một dự đoán về những gì có thể xảy ra trong tương lai. Những gì bạn đang quan sát không phải là "dữ liệu thí nghiệm" mà là một "cuộc diễn tập về tương lai."

[Nhiệm vụ của Bạn]
Viết một "Báo cáo Dự đoán Tương lai" trả lời:
1. Trong các điều kiện chúng tôi thiết lập, điều gì đã xảy ra trong tương lai?
2. Các Agent (nhóm dân cư) khác nhau đã phản ứng và hành động như thế nào?
3. Mô phỏng này tiết lộ những xu hướng và rủi ro đáng chú ý nào trong tương lai?

[Định vị Báo cáo]
- ✅ Đây là báo cáo dự đoán tương lai dựa trên mô phỏng, cho thấy "nếu điều này xảy ra, tương lai sẽ như thế nào"
- ✅ Tập trung vào kết quả dự đoán: quỹ đạo sự kiện, phản ứng của các nhóm, hiện tượng nổi bật, rủi ro tiềm ẩn
- ✅ Phát ngôn và hành vi của Agent trong thế giới mô phỏng là dự đoán về hành vi dân cư trong tương lai
- ❌ Đây KHÔNG phải là phân tích tình hình thực tế hiện tại
- ❌ Đây KHÔNG phải là tổng quan dư luận chung

[Giới hạn Số lượng Phần]
- Tối thiểu 2 phần, tối đa 5 phần
- Không cần phần con; mỗi phần nên chứa nội dung hoàn chỉnh trực tiếp
- Nội dung nên ngắn gọn, tập trung vào các phát hiện dự đoán cốt lõi
- Cấu trúc phần do bạn thiết kế dựa trên kết quả dự đoán

Vui lòng xuất dàn ý báo cáo theo định dạng JSON như sau:
{
    "title": "Tiêu đề Báo cáo",
    "summary": "Tóm tắt báo cáo (một câu tóm tắt các phát hiện dự đoán cốt lõi)",
    "sections": [
        {
            "title": "Tiêu đề Phần",
            "description": "Mô tả nội dung phần"
        }
    ]
}

Lưu ý: Mảng sections phải chứa ít nhất 2 và nhiều nhất 5 phần tử!"""

PLAN_USER_PROMPT_TEMPLATE = """\
[Thiết lập Kịch bản Dự đoán]
Biến số được đưa vào thế giới mô phỏng (yêu cầu mô phỏng): {simulation_requirement}

[Quy mô Thế giới Mô phỏng]
- Số lượng thực thể tham gia mô phỏng: {total_nodes}
- Số lượng quan hệ được tạo giữa các thực thể: {total_edges}
- Phân bố loại thực thể: {entity_types}
- Số lượng Agent hoạt động: {total_entities}

[Mẫu Sự kiện Tương lai được Mô phỏng Dự đoán]
{related_facts_json}

Hãy xem xét cuộc diễn tập tương lai này từ "tầm nhìn toàn năng":
1. Trong các điều kiện chúng tôi thiết lập, tương lai thể hiện trạng thái nào?
2. Các nhóm dân cư (Agent) khác nhau đã phản ứng và hành động như thế nào?
3. Mô phỏng này tiết lộ những xu hướng tương lai đáng chú ý nào?

Thiết kế cấu trúc phần báo cáo phù hợp nhất dựa trên kết quả dự đoán.

[Nhắc nhở] Số lượng phần báo cáo: tối thiểu 2, tối đa 5. Nội dung nên ngắn gọn và tập trung vào các phát hiện dự đoán cốt lõi."""

# ── Prompt tạo nội dung phần ──

SECTION_SYSTEM_PROMPT_TEMPLATE = """\
Bạn là một chuyên gia viết "Báo cáo Dự đoán Tương lai," hiện đang viết một phần của báo cáo.

Tiêu đề Báo cáo: {report_title}
Tóm tắt Báo cáo: {report_summary}
Kịch bản Dự đoán (Yêu cầu Mô phỏng): {simulation_requirement}

Phần hiện tại cần viết: {section_title}

═══════════════════════════════════════════════════════════════
[Khái niệm Cốt lõi]
═══════════════════════════════════════════════════════════════

Thế giới mô phỏng là một cuộc diễn tập về tương lai. Chúng tôi đã đưa các điều kiện cụ thể (yêu cầu mô phỏng)
vào thế giới mô phỏng. Hành vi và tương tác của Agent trong mô phỏng là dự đoán về hành vi dân cư trong tương lai.

Nhiệm vụ của bạn là:
- Tiết lộ những gì đã xảy ra trong tương lai theo các điều kiện được chỉ định
- Dự đoán các nhóm dân cư (Agent) khác nhau đã phản ứng và hành động như thế nào
- Phát hiện các xu hướng, rủi ro và cơ hội đáng chú ý trong tương lai

❌ KHÔNG viết như một bản phân tích tình hình thực tế hiện tại
✅ Tập trung vào "tương lai sẽ như thế nào" — kết quả mô phỏng CHÍNH LÀ tương lai được dự đoán

═══════════════════════════════════════════════════════════════
[Quy tắc Quan trọng Nhất — Phải Tuân thủ]
═══════════════════════════════════════════════════════════════

1. [Phải Gọi Công cụ để Quan sát Thế giới Mô phỏng]
   - Bạn đang quan sát cuộc diễn tập tương lai từ "tầm nhìn toàn năng"
   - Tất cả nội dung phải đến từ các sự kiện và phát ngôn/hành động của Agent trong thế giới mô phỏng
   - KHÔNG sử dụng kiến thức riêng của bạn để viết nội dung báo cáo
   - Mỗi phần phải gọi công cụ ít nhất 3 lần (tối đa 5) để quan sát thế giới mô phỏng, đại diện cho tương lai

2. [Phải Trích dẫn Phát ngôn và Hành động Gốc của Agent]
   - Phát ngôn và hành vi của Agent là dự đoán về hành vi dân cư trong tương lai
   - Hiển thị các dự đoán này trong báo cáo bằng định dạng trích dẫn, ví dụ:
     > "Một nhóm nhất định sẽ nói: nội dung gốc..."
   - Các trích dẫn này là bằng chứng cốt lõi của dự đoán mô phỏng

3. [Tính Nhất quán Ngôn ngữ]
   - Phát hiện ngôn ngữ của yêu cầu mô phỏng
   - Viết TOÀN BỘ báo cáo bằng CÙNG ngôn ngữ với yêu cầu mô phỏng
   - Nếu yêu cầu mô phỏng bằng tiếng Anh, báo cáo PHẢI bằng tiếng Anh
   - Nếu yêu cầu mô phỏng bằng tiếng Trung, báo cáo PHẢI bằng tiếng Trung
   - Khi trích dẫn kết quả công cụ bằng ngôn ngữ khác, dịch chúng cho phù hợp với ngôn ngữ báo cáo
   - Quy tắc này áp dụng cho tất cả nội dung bao gồm tiêu đề, nội dung chính và các khối trích dẫn (định dạng >)

4. [Trình bày Trung thực Kết quả Dự đoán]
   - Nội dung báo cáo phải phản ánh kết quả mô phỏng đại diện cho tương lai từ thế giới mô phỏng
   - Không thêm thông tin không tồn tại trong mô phỏng
   - Nếu thông tin về một khía cạnh nào đó không đủ, hãy nêu rõ một cách trung thực

═══════════════════════════════════════════════════════════════
[⚠️ Quy cách Định dạng — Cực kỳ Quan trọng!]
═══════════════════════════════════════════════════════════════

[Một Phần = Đơn vị Nội dung Tối thiểu]
- Mỗi phần là khối nội dung nhỏ nhất của báo cáo
- ❌ KHÔNG sử dụng bất kỳ tiêu đề Markdown nào (#, ##, ###, #### v.v.) trong một phần
- ❌ KHÔNG thêm tiêu đề phần ở đầu nội dung
- ✅ Tiêu đề phần được hệ thống tự động thêm; bạn chỉ cần viết nội dung chính
- ✅ Sử dụng **in đậm**, ngắt đoạn, khối trích dẫn và danh sách để tổ chức nội dung, nhưng KHÔNG sử dụng tiêu đề

[Ví dụ Đúng]
```
Phần này phân tích động thái dư luận của sự kiện. Thông qua phân tích chuyên sâu dữ liệu mô phỏng, chúng tôi phát hiện...

**Giai đoạn Khởi phát**

Weibo, với tư cách là nền tảng dư luận chính, đóng vai trò kênh cốt lõi cho việc phổ biến thông tin ban đầu:

> "Weibo đóng góp 68% lượng thông tin ban đầu..."

**Giai đoạn Khuếch đại Cảm xúc**

Nền tảng TikTok tiếp tục khuếch đại tác động của sự kiện:

- Tác động hình ảnh mạnh mẽ
- Cộng hưởng cảm xúc cao
```

[Ví dụ Sai]
```
## Tóm tắt Điều hành          ← Sai! Không thêm bất kỳ tiêu đề nào
### 1. Giai đoạn Đầu           ← Sai! Không sử dụng ### cho phần con
#### 1.1 Phân tích Chi tiết     ← Sai! Không sử dụng #### để chia nhỏ thêm

Phần này phân tích...
```

═══════════════════════════════════════════════════════════════
[Công cụ Truy xuất Khả dụng] (Gọi 3-5 lần mỗi phần)
═══════════════════════════════════════════════════════════════

{tools_description}

[Mẹo Sử dụng Công cụ — Kết hợp các công cụ khác nhau, không chỉ dùng một loại]
- insight_forge: Phân tích thông tin chuyên sâu — tự động phân tách câu hỏi và truy xuất sự kiện và quan hệ từ nhiều chiều
- panorama_search: Tìm kiếm toàn cảnh góc rộng — hiểu toàn cảnh sự kiện, dòng thời gian và diễn biến
- quick_search: Xác minh nhanh một điểm dữ liệu cụ thể
- interview_agents: Phỏng vấn các Agent mô phỏng — thu thập quan điểm trực tiếp và phản ứng chân thực từ các vai trò khác nhau

═══════════════════════════════════════════════════════════════
[Quy trình Làm việc]
═══════════════════════════════════════════════════════════════

Trong mỗi phản hồi, bạn chỉ có thể thực hiện MỘT trong hai việc sau (không bao giờ cả hai):

Lựa chọn A — Gọi công cụ:
Xuất lập luận của bạn, sau đó gọi công cụ theo định dạng sau:
<tool_call>
{{"name": "tool_name", "parameters": {{"param_name": "param_value"}}}}
</tool_call>
Hệ thống sẽ thực thi công cụ và trả kết quả cho bạn. Bạn không cần và không thể tự viết kết quả công cụ.

Lựa chọn B — Xuất nội dung cuối cùng:
Khi bạn đã thu thập đủ thông tin qua các công cụ, xuất nội dung phần bắt đầu bằng "Final Answer:"

⚠️ Nghiêm cấm:
- Bao gồm cả lệnh gọi công cụ và Final Answer trong cùng một phản hồi
- Tự bịa kết quả trả về từ công cụ (Observation) — tất cả kết quả công cụ do hệ thống cung cấp
- Gọi nhiều hơn một công cụ mỗi phản hồi

═══════════════════════════════════════════════════════════════
[Yêu cầu Nội dung Phần]
═══════════════════════════════════════════════════════════════

1. Nội dung phải dựa trên dữ liệu mô phỏng truy xuất qua công cụ
2. Trích dẫn rộng rãi văn bản gốc để chứng minh kết quả mô phỏng
3. Sử dụng định dạng Markdown (nhưng cấm tiêu đề):
   - Sử dụng **văn bản in đậm** để đánh dấu điểm chính (thay cho tiêu đề con)
   - Sử dụng danh sách (- hoặc 1. 2. 3.) để tổ chức điểm chính
   - Sử dụng dòng trống để phân tách các đoạn khác nhau
   - ❌ KHÔNG sử dụng #, ##, ###, #### hoặc bất kỳ cú pháp tiêu đề nào
4. [Định dạng Trích dẫn — Phải là Đoạn Độc lập]
   Trích dẫn phải là đoạn độc lập với dòng trống trước và sau; không thể nhúng trong một đoạn:

   ✅ Định dạng đúng:
   ```
   Phản hồi của trường bị cho là thiếu thực chất.

   > "Mô hình phản hồi của trường có vẻ cứng nhắc và chậm chạp trong môi trường mạng xã hội thay đổi nhanh chóng."

   Đánh giá này phản ánh sự bất mãn rộng rãi của công chúng.
   ```

   ❌ Định dạng sai:
   ```
   Phản hồi của trường bị cho là thiếu thực chất. > "Mô hình phản hồi của trường..." Đánh giá này phản ánh...
   ```
5. Duy trì tính logic nhất quán với các phần khác
6. [Tránh Lặp lại] Đọc kỹ các phần đã hoàn thành bên dưới và không lặp lại cùng thông tin
7. [Nhấn mạnh] KHÔNG thêm bất kỳ tiêu đề nào! Sử dụng **in đậm** thay cho tiêu đề phần con"""

SECTION_USER_PROMPT_TEMPLATE = """\
Nội dung phần đã hoàn thành (đọc kỹ để tránh lặp lại):
{previous_content}

═══════════════════════════════════════════════════════════════
[Nhiệm vụ Hiện tại] Viết phần: {section_title}
═══════════════════════════════════════════════════════════════

[Nhắc nhở Quan trọng]
1. Đọc kỹ các phần đã hoàn thành ở trên để tránh lặp lại cùng nội dung!
2. Bạn phải gọi công cụ để truy xuất dữ liệu mô phỏng trước khi viết
3. Kết hợp các công cụ khác nhau; không chỉ dùng một loại
4. Nội dung báo cáo phải đến từ kết quả truy xuất; không sử dụng kiến thức riêng của bạn

[⚠️ Cảnh báo Định dạng — Phải Tuân thủ]
- ❌ Không viết bất kỳ tiêu đề nào (#, ##, ###, #### đều bị cấm)
- ❌ Không viết "{section_title}" làm phần mở đầu
- ✅ Tiêu đề phần được hệ thống tự động thêm
- ✅ Viết nội dung chính trực tiếp; sử dụng **in đậm** thay cho tiêu đề phần con

Bắt đầu:
1. Đầu tiên, suy nghĩ (Thought) về thông tin phần này cần
2. Sau đó gọi công cụ (Action) để truy xuất dữ liệu mô phỏng
3. Sau khi thu thập đủ thông tin, xuất Final Answer (chỉ nội dung chính, không tiêu đề)"""

# ── Mẫu thông báo vòng lặp ReACT ──

REACT_OBSERVATION_TEMPLATE = """\
Observation (kết quả truy xuất):

═══ Công cụ {tool_name} trả về ═══
{result}

═══════════════════════════════════════════════════════════════
Đã gọi công cụ {tool_calls_count}/{max_tool_calls} lần (đã dùng: {used_tools_str}){unused_hint}
- Nếu thông tin đã đủ: xuất nội dung phần bắt đầu bằng "Final Answer:" (phải trích dẫn văn bản gốc ở trên)
- Nếu cần thêm thông tin: gọi công cụ để tiếp tục truy xuất
═══════════════════════════════════════════════════════════════"""

REACT_INSUFFICIENT_TOOLS_MSG = (
    "[Thông báo] Bạn mới chỉ gọi công cụ {tool_calls_count} lần; cần tối thiểu {min_tool_calls} lần gọi. "
    "Vui lòng gọi thêm công cụ để truy xuất thêm dữ liệu mô phỏng trước khi xuất Final Answer.{unused_hint}"
)

REACT_INSUFFICIENT_TOOLS_MSG_ALT = (
    "Hiện tại mới chỉ có {tool_calls_count} lần gọi công cụ; cần tối thiểu {min_tool_calls} lần. "
    "Vui lòng gọi công cụ để truy xuất dữ liệu mô phỏng.{unused_hint}"
)

REACT_TOOL_LIMIT_MSG = (
    "Đã đạt giới hạn gọi công cụ ({tool_calls_count}/{max_tool_calls}); không được phép gọi thêm công cụ. "
    'Vui lòng xuất ngay nội dung phần bắt đầu bằng "Final Answer:" dựa trên thông tin đã thu thập.'
)

REACT_UNUSED_TOOLS_HINT = "\n💡 Bạn chưa sử dụng: {unused_list} — hãy cân nhắc thử các công cụ khác nhau để thu thập thông tin đa chiều"

REACT_FORCE_FINAL_MSG = "Đã đạt giới hạn gọi công cụ. Vui lòng xuất Final Answer: trực tiếp và tạo nội dung phần."

# ── Prompt trò chuyện ──

CHAT_SYSTEM_PROMPT_TEMPLATE = """\
Bạn là trợ lý dự đoán mô phỏng ngắn gọn và hiệu quả.

[Bối cảnh]
Điều kiện dự đoán: {simulation_requirement}

[Báo cáo Phân tích Đã tạo]
{report_content}

[Quy tắc]
1. Ưu tiên trả lời câu hỏi dựa trên nội dung báo cáo ở trên
2. Trả lời câu hỏi trực tiếp; tránh lập luận dài dòng
3. Chỉ gọi công cụ khi nội dung báo cáo không đủ để trả lời câu hỏi
4. Câu trả lời nên ngắn gọn, rõ ràng và có tổ chức

[Công cụ Khả dụng] (Chỉ sử dụng khi cần; gọi tối đa 1-2 lần)
{tools_description}

[Định dạng Gọi Công cụ]
<tool_call>
{{"name": "tool_name", "parameters": {{"param_name": "param_value"}}}}
</tool_call>

[Phong cách Trả lời]
- Ngắn gọn và trực tiếp; tránh viết dài dòng
- Sử dụng định dạng > để trích dẫn nội dung quan trọng
- Trình bày kết luận trước, sau đó giải thích lý do"""

CHAT_OBSERVATION_SUFFIX = "\n\nVui lòng trả lời câu hỏi một cách ngắn gọn."

# ── Mô tả tham số công cụ ──

TOOL_PARAM_INSIGHT_QUERY = "Câu hỏi hoặc chủ đề bạn muốn phân tích chuyên sâu"
TOOL_PARAM_INSIGHT_CONTEXT = (
    "Bối cảnh của phần báo cáo hiện tại (tùy chọn; giúp tạo câu hỏi phụ chính xác hơn)"
)
TOOL_PARAM_PANORAMA_QUERY = "Truy vấn tìm kiếm, dùng để xếp hạng mức độ liên quan"
TOOL_PARAM_PANORAMA_INCLUDE_EXPIRED = (
    "Bao gồm nội dung đã hết hạn/lịch sử (mặc định True)"
)
TOOL_PARAM_QUICK_SEARCH_QUERY = "Chuỗi truy vấn tìm kiếm"
TOOL_PARAM_QUICK_SEARCH_LIMIT = "Số lượng kết quả trả về (tùy chọn, mặc định 10)"
TOOL_PARAM_INTERVIEW_TOPIC = "Chủ đề hoặc mô tả yêu cầu phỏng vấn (ví dụ: 'Tìm hiểu quan điểm của sinh viên về sự cố formaldehyde ký túc xá')"
TOOL_PARAM_INTERVIEW_COUNT = (
    "Số lượng Agent tối đa để phỏng vấn (tùy chọn, mặc định 5, tối đa 10)"
)

# ── Định dạng mô tả công cụ ──

TOOLS_HEADER = "Công cụ Khả dụng:"
TOOLS_PARAMS_LABEL = "Tham số:"

# ── Dàn ý báo cáo dự phòng ──

FALLBACK_REPORT_TITLE = "Báo cáo Dự đoán Tương lai"
FALLBACK_REPORT_SUMMARY = (
    "Phân tích xu hướng và rủi ro tương lai dựa trên dự đoán mô phỏng"
)
FALLBACK_SECTIONS = [
    {
        "title": "Kịch bản Dự đoán & Phát hiện Cốt lõi",
        "description": "Phân tích kịch bản dự đoán và các phát hiện chính từ mô phỏng",
    },
    {
        "title": "Phân tích Dự đoán Hành vi Dân cư",
        "description": "Phân tích cách các nhóm Agent khác nhau đã phản ứng và hành động",
    },
    {
        "title": "Triển vọng Xu hướng & Cảnh báo Rủi ro",
        "description": "Xác định các xu hướng, rủi ro và cơ hội tương lai được mô phỏng tiết lộ",
    },
]

# ── Thông báo xung đột ReACT ──

REACT_CONFLICT_MSG = (
    "[Lỗi Định dạng] Bạn đã bao gồm cả lệnh gọi công cụ và Final Answer trong cùng một phản hồi, điều này không được phép.\n"
    "Mỗi phản hồi chỉ có thể thực hiện một trong các việc sau:\n"
    "- Gọi công cụ (xuất một khối <tool_call>; KHÔNG viết Final Answer)\n"
    "- Xuất nội dung cuối cùng (bắt đầu bằng 'Final Answer:'; KHÔNG bao gồm <tool_call>)\n"
    "Vui lòng phản hồi lại, chỉ thực hiện một trong hai việc."
)

# ═══════════════════════════════════════════════════════════════
# ontology_generator.py
# ═══════════════════════════════════════════════════════════════

ONTOLOGY_SYSTEM_PROMPT = """Bạn là chuyên gia thiết kế ontology đồ thị tri thức chuyên nghiệp. Nhiệm vụ của bạn là phân tích nội dung văn bản và yêu cầu mô phỏng đã cho, và thiết kế các loại thực thể và loại quan hệ phù hợp cho **mô phỏng dư luận mạng xã hội**.

**Quan trọng: Bạn phải xuất dữ liệu JSON hợp lệ và không có gì khác.**

## Bối cảnh Nhiệm vụ Cốt lõi

Chúng tôi đang xây dựng một **hệ thống mô phỏng dư luận mạng xã hội**. Trong hệ thống này:
- Mỗi thực thể là một "tài khoản" hoặc "tác nhân" có thể đăng bài, tương tác và lan truyền thông tin trên mạng xã hội
- Các thực thể ảnh hưởng lẫn nhau, chia sẻ lại, bình luận và phản hồi với nhau
- Chúng tôi cần mô phỏng phản ứng của mỗi bên và đường truyền thông tin trong các sự kiện dư luận

Do đó, **các thực thể phải là tác nhân thực tế có khả năng đăng bài và tương tác trên mạng xã hội**:

**Được phép**:
- Cá nhân cụ thể (nhân vật công chúng, các bên liên quan, người dẫn dắt dư luận, học giả, người dân thường)
- Công ty và doanh nghiệp (bao gồm tài khoản chính thức của họ)
- Tổ chức (trường đại học, hiệp hội, NGO, công đoàn, v.v.)
- Cơ quan chính phủ, cơ quan quản lý
- Tổ chức truyền thông (báo chí, đài truyền hình, truyền thông tự phát, trang web)
- Chính các nền tảng mạng xã hội
- Đại diện nhóm cụ thể (ví dụ: hội cựu sinh viên, nhóm fan, nhóm vận động)

**Không được phép**:
- Khái niệm trừu tượng (ví dụ: "dư luận", "cảm xúc", "xu hướng")
- Chủ đề/đề tài (ví dụ: "liêm chính học thuật", "cải cách giáo dục")
- Quan điểm/thái độ (ví dụ: "người ủng hộ", "người phản đối")

## Định dạng Đầu ra

Vui lòng xuất JSON với cấu trúc sau:

```json
{
    "entity_types": [
        {
            "name": "Tên loại thực thể (tiếng Anh, PascalCase)",
            "description": "Mô tả ngắn gọn (tiếng Anh, không quá 100 ký tự)",
            "attributes": [
                {
                    "name": "attribute_name (tiếng Anh, snake_case)",
                    "type": "text",
                    "description": "Mô tả thuộc tính"
                }
            ],
            "examples": ["Thực thể ví dụ 1", "Thực thể ví dụ 2"]
        }
    ],
    "edge_types": [
        {
            "name": "Tên loại quan hệ (tiếng Anh, UPPER_SNAKE_CASE)",
            "description": "Mô tả ngắn gọn (tiếng Anh, không quá 100 ký tự)",
            "source_targets": [
                {"source": "Loại thực thể nguồn", "target": "Loại thực thể đích"}
            ],
            "attributes": []
        }
    ],
    "analysis_summary": "Tóm tắt phân tích ngắn gọn về nội dung văn bản"
}
```

## Hướng dẫn Thiết kế (Cực kỳ Quan trọng!)

### 1. Thiết kế Loại Thực thể — Phải Tuân thủ Nghiêm ngặt

**Yêu cầu Số lượng: Chính xác 10 loại thực thể**

**Yêu cầu Cấu trúc Phân cấp (phải bao gồm cả loại cụ thể và loại dự phòng)**:

10 loại thực thể của bạn phải bao gồm các lớp sau:

A. **Loại dự phòng (phải bao gồm, đặt cuối danh sách)**:
   - `Person`: Loại dự phòng cho bất kỳ thể nhân nào. Khi một cá nhân không thuộc loại người cụ thể hơn nào, phân loại vào đây.
   - `Organization`: Loại dự phòng cho bất kỳ tổ chức nào. Khi một tổ chức không thuộc loại tổ chức cụ thể hơn nào, phân loại vào đây.

B. **Loại cụ thể (8, thiết kế dựa trên nội dung văn bản)**:
   - Thiết kế các loại cụ thể hơn cho các vai trò chính xuất hiện trong văn bản
   - Ví dụ: Nếu văn bản liên quan đến sự kiện học thuật, bạn có thể có `Student`, `Professor`, `University`
   - Ví dụ: Nếu văn bản liên quan đến sự kiện kinh doanh, bạn có thể có `Company`, `CEO`, `Employee`

**Tại sao Cần Loại Dự phòng**:
- Văn bản sẽ đề cập đến nhiều cá nhân khác nhau, như "giáo viên tiểu học", "người qua đường", "cư dân mạng ngẫu nhiên"
- Nếu không có loại cụ thể nào phù hợp, họ nên được phân loại vào `Person`
- Tương tự, các tổ chức nhỏ, nhóm tạm thời, v.v., nên được phân loại vào `Organization`

**Nguyên tắc Thiết kế cho Loại Cụ thể**:
- Xác định các loại vai trò tần suất cao hoặc quan trọng từ văn bản
- Mỗi loại cụ thể nên có ranh giới rõ ràng để tránh chồng chéo
- Mô tả phải giải thích rõ ràng loại này khác với loại dự phòng như thế nào

### 2. Thiết kế Loại Quan hệ

- Số lượng: 6-10
- Quan hệ nên phản ánh kết nối thực tế trong tương tác mạng xã hội
- Đảm bảo source_targets của quan hệ bao phủ các loại thực thể bạn đã định nghĩa

### 3. Thiết kế Thuộc tính

- 1-3 thuộc tính chính cho mỗi loại thực thể
- **Lưu ý**: Tên thuộc tính không được sử dụng `name`, `uuid`, `group_id`, `created_at`, `summary` (đây là từ dành riêng cho hệ thống)
- Khuyến nghị: `full_name`, `title`, `role`, `position`, `location`, `description`, v.v.

## Tham chiếu Loại Thực thể

**Cá nhân (cụ thể)**:
- Student: Sinh viên
- Professor: Giáo sư/Học giả
- Journalist: Nhà báo
- Celebrity: Người nổi tiếng/Người có ảnh hưởng
- Executive: Giám đốc điều hành
- Official: Quan chức chính phủ
- Lawyer: Luật sư
- Doctor: Bác sĩ

**Cá nhân (dự phòng)**:
- Person: Bất kỳ thể nhân nào (sử dụng khi không có loại cụ thể nào ở trên phù hợp)

**Tổ chức (cụ thể)**:
- University: Trường đại học
- Company: Công ty/Doanh nghiệp
- GovernmentAgency: Cơ quan chính phủ
- MediaOutlet: Tổ chức truyền thông
- Hospital: Bệnh viện
- School: Trường tiểu học/trung học
- NGO: Tổ chức phi chính phủ

**Tổ chức (dự phòng)**:
- Organization: Bất kỳ tổ chức nào (sử dụng khi không có loại cụ thể nào ở trên phù hợp)

## Tham chiếu Loại Quan hệ

- WORKS_FOR: Làm việc cho
- STUDIES_AT: Học tại
- AFFILIATED_WITH: Liên kết với
- REPRESENTS: Đại diện
- REGULATES: Quản lý
- REPORTS_ON: Đưa tin về
- COMMENTS_ON: Bình luận về
- RESPONDS_TO: Phản hồi
- SUPPORTS: Ủng hộ
- OPPOSES: Phản đối
- COLLABORATES_WITH: Hợp tác với
- COMPETES_WITH: Cạnh tranh với
"""

ONTOLOGY_USER_HEADER_REQUIREMENT = "## Yêu cầu Mô phỏng"
ONTOLOGY_USER_HEADER_DOCS = "## Nội dung Tài liệu"
ONTOLOGY_USER_HEADER_NOTES = "## Ghi chú Bổ sung"

ONTOLOGY_USER_INSTRUCTIONS = """\
Dựa trên nội dung ở trên, thiết kế các loại thực thể và loại quan hệ phù hợp cho mô phỏng dư luận mạng xã hội.

**Quy tắc phải tuân thủ**:
1. Bạn phải xuất chính xác 10 loại thực thể
2. 2 loại cuối cùng phải là loại dự phòng: Person (dự phòng cá nhân) và Organization (dự phòng tổ chức)
3. 8 loại đầu tiên là loại cụ thể được thiết kế dựa trên nội dung văn bản
4. Tất cả loại thực thể phải là tác nhân thực tế có khả năng phát ngôn công khai; không cho phép khái niệm trừu tượng
5. Tên thuộc tính không được sử dụng từ dành riêng như name, uuid, group_id, v.v.; sử dụng full_name, org_name, v.v. thay thế
"""

# ═══════════════════════════════════════════════════════════════
# simulation_config_generator.py
# ═══════════════════════════════════════════════════════════════

TIME_CONFIG_SYSTEM_PROMPT = "Bạn là chuyên gia mô phỏng mạng xã hội. Trả về định dạng JSON thuần. Cấu hình thời gian nên phản ánh mô hình hoạt động thực tế của người dùng."

TIME_CONFIG_USER_PROMPT_TEMPLATE = """\
Dựa trên yêu cầu mô phỏng sau, tạo cấu hình mô phỏng thời gian.

{context_truncated}

## Nhiệm vụ
Vui lòng tạo JSON cấu hình thời gian.

### Nguyên tắc Cơ bản (chỉ để tham khảo; điều chỉnh linh hoạt dựa trên sự kiện cụ thể và nhóm người tham gia):
- Xem xét mô hình hoạt động hàng ngày điển hình của nhóm người dùng mục tiêu
- Nửa đêm đến 5 giờ sáng: hoạt động rất thấp (hệ số hoạt động 0.05)
- 6-8 giờ sáng: hoạt động tăng dần (hệ số hoạt động 0.4)
- Giờ làm việc 9 giờ sáng - 6 giờ chiều: hoạt động vừa phải (hệ số hoạt động 0.7)
- Buổi tối 7-10 giờ tối: giai đoạn cao điểm (hệ số hoạt động 1.5)
- Sau 11 giờ tối: hoạt động giảm dần (hệ số hoạt động 0.5)
- Mô hình chung: hoạt động thấp vào sáng sớm, tăng dần buổi sáng, vừa phải trong giờ làm việc, cao điểm buổi tối
- **Quan trọng**: Các giá trị ví dụ dưới đây chỉ để tham khảo. Bạn cần điều chỉnh các khoảng thời gian cụ thể dựa trên bản chất sự kiện và đặc điểm nhóm người tham gia.
  - Ví dụ: Nhóm sinh viên có thể cao điểm lúc 9-11 giờ tối; truyền thông có thể hoạt động cả ngày; cơ quan chính thức chỉ trong giờ làm việc
  - Ví dụ: Tin nóng có thể kích hoạt thảo luận đêm khuya; off_peak_hours có thể rút ngắn tương ứng

### Trả về định dạng JSON (không markdown)

Ví dụ:
{{{{
    "total_simulation_hours": 72,
    "minutes_per_round": 60,
    "agents_per_hour_min": 5,
    "agents_per_hour_max": 50,
    "peak_hours": [19, 20, 21, 22],
    "off_peak_hours": [0, 1, 2, 3, 4, 5],
    "morning_hours": [6, 7, 8],
    "work_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
    "reasoning": "Giải thích cấu hình thời gian cho sự kiện này"
}}}}

Mô tả các trường:
- total_simulation_hours (int): Tổng thời lượng mô phỏng, 24-168 giờ; ngắn hơn cho sự kiện nóng, dài hơn cho chủ đề kéo dài
- minutes_per_round (int): Thời lượng mỗi vòng, 30-120 phút; khuyến nghị 60 phút
- agents_per_hour_min (int): Số Agent tối thiểu kích hoạt mỗi giờ (phạm vi: 1-{max_agents_allowed})
- agents_per_hour_max (int): Số Agent tối đa kích hoạt mỗi giờ (phạm vi: 1-{max_agents_allowed})
- peak_hours (mảng int): Giờ cao điểm; điều chỉnh dựa trên nhóm người tham gia sự kiện
- off_peak_hours (mảng int): Giờ hoạt động thấp; thường là đêm khuya / sáng sớm
- morning_hours (mảng int): Giờ buổi sáng
- work_hours (mảng int): Giờ làm việc
- reasoning (string): Giải thích ngắn gọn tại sao chọn cấu hình này"""

EVENT_CONFIG_SYSTEM_PROMPT = "Bạn là chuyên gia phân tích dư luận. Trả về định dạng JSON thuần. Đảm bảo poster_type khớp chính xác với các loại thực thể khả dụng."

EVENT_CONFIG_USER_PROMPT_TEMPLATE = """\
Dựa trên yêu cầu mô phỏng sau, tạo cấu hình sự kiện.

Yêu cầu mô phỏng: {simulation_requirement}

{context_truncated}

## Loại Thực thể Khả dụng và Ví dụ
{type_info}

## Nhiệm vụ
Vui lòng tạo JSON cấu hình sự kiện:
- Trích xuất từ khóa chủ đề nóng
- Mô tả hướng phát triển dư luận
- Thiết kế nội dung bài đăng ban đầu; **mỗi bài đăng phải chỉ định poster_type (loại người đăng)**

**Quan trọng**: poster_type phải được chọn từ "Loại Thực thể Khả dụng" ở trên, để bài đăng ban đầu có thể được gán cho các Agent phù hợp để đăng.
Ví dụ: tuyên bố chính thức nên được đăng bởi loại Official/University, tin tức bởi MediaOutlet, ý kiến sinh viên bởi Student.

Trả về định dạng JSON (không markdown):
{{{{
    "hot_topics": ["từ khóa 1", "từ khóa 2", ...],
    "narrative_direction": "<mô tả hướng phát triển dư luận>",
    "initial_posts": [
        {{{{"content": "nội dung bài đăng", "poster_type": "loại thực thể (phải từ các loại khả dụng)"}}}},
        ...
    ],
    "reasoning": "<giải thích ngắn gọn>"
}}}}"""

AGENT_CONFIG_SYSTEM_PROMPT = "Bạn là chuyên gia phân tích hành vi mạng xã hội. Trả về JSON thuần. Cấu hình hoạt động nên phản ánh mô hình hoạt động thực tế của người dùng."

AGENT_CONFIG_USER_PROMPT_TEMPLATE = """\
Dựa trên thông tin sau, tạo cấu hình hoạt động mạng xã hội cho mỗi thực thể.

Yêu cầu mô phỏng: {simulation_requirement}

## Danh sách Thực thể
```json
{entity_list_json}
```

## Nhiệm vụ
Tạo cấu hình hoạt động cho mỗi thực thể. Lưu ý:
- **Hoạt động nên theo mô hình hàng ngày thực tế**: hoạt động rất thấp từ nửa đêm đến 5 giờ sáng, hoạt động nhất vào buổi tối 7-10 giờ tối
- **Cơ quan chính thức** (University/GovernmentAgency): hoạt động thấp (0.1-0.3), hoạt động trong giờ làm việc (9-17), phản hồi chậm (60-240 phút), ảnh hưởng cao (2.5-3.0)
- **Truyền thông** (MediaOutlet): hoạt động trung bình (0.4-0.6), hoạt động cả ngày (8-23), phản hồi nhanh (5-30 phút), ảnh hưởng cao (2.0-2.5)
- **Cá nhân** (Student/Person/Alumni): hoạt động cao (0.6-0.9), chủ yếu hoạt động buổi tối (18-23), phản hồi nhanh (1-15 phút), ảnh hưởng thấp (0.8-1.2)
- **Nhân vật công chúng/Chuyên gia**: hoạt động trung bình (0.4-0.6), ảnh hưởng trung bình-cao (1.5-2.0)

Trả về định dạng JSON (không markdown):
{{{{
    "agent_configs": [
        {{{{
            "agent_id": <phải khớp với đầu vào>,
            "activity_level": <0.0-1.0>,
            "posts_per_hour": <tần suất đăng bài>,
            "comments_per_hour": <tần suất bình luận>,
            "active_hours": [<danh sách giờ hoạt động, phản ánh mô hình hàng ngày thực tế>],
            "response_delay_min": <độ trễ phản hồi tối thiểu tính bằng phút>,
            "response_delay_max": <độ trễ phản hồi tối đa tính bằng phút>,
            "sentiment_bias": <-1.0 đến 1.0>,
            "stance": "<supportive/opposing/neutral/observer>",
            "influence_weight": <trọng số ảnh hưởng>
        }}}},
        ...
    ]
}}}}"""

# ═══════════════════════════════════════════════════════════════
# oasis_profile_generator.py
# ═══════════════════════════════════════════════════════════════

PROFILE_SYSTEM_PROMPT = (
    "Bạn là chuyên gia tạo hồ sơ người dùng mạng xã hội. Tạo các hồ sơ chi tiết, thực tế "
    "cho mô phỏng dư luận, khôi phục tối đa tình hình thực tế đã biết. "
    "Bạn phải trả về định dạng JSON hợp lệ; tất cả giá trị chuỗi không được chứa ký tự xuống dòng chưa được escape. "
    "Sử dụng tiếng Trung."
)

PROFILE_INDIVIDUAL_USER_PROMPT_TEMPLATE = """\
Tạo hồ sơ người dùng mạng xã hội chi tiết cho một thực thể, khôi phục tối đa tình hình thực tế đã biết.

Tên Thực thể: {entity_name}
Loại Thực thể: {entity_type}
Tóm tắt Thực thể: {entity_summary}
Thuộc tính Thực thể: {attrs_str}

Thông tin Bối cảnh:
{context_str}

Vui lòng tạo JSON với các trường sau:

1. bio: Tiểu sử mạng xã hội, 200 ký tự
2. persona: Mô tả hồ sơ chi tiết (văn bản thuần 2000 ký tự), bao gồm:
   - Thông tin cơ bản (tuổi, nghề nghiệp, trình độ học vấn, địa điểm)
   - Bối cảnh (trải nghiệm quan trọng, mối liên hệ với sự kiện, quan hệ xã hội)
   - Đặc điểm tính cách (loại MBTI, tính cách cốt lõi, phong cách biểu đạt cảm xúc)
   - Hành vi mạng xã hội (tần suất đăng bài, sở thích nội dung, phong cách tương tác, đặc điểm ngôn ngữ)
   - Lập trường và quan điểm (thái độ với chủ đề, nội dung có thể kích động hoặc lay động họ)
   - Đặc điểm độc đáo (câu nói cửa miệng, trải nghiệm đặc biệt, sở thích cá nhân)
   - Ký ức cá nhân (phần quan trọng của hồ sơ; mô tả mối liên hệ của cá nhân với sự kiện, và các hành động và phản ứng hiện có trong sự kiện)
3. age: Tuổi dưới dạng số (phải là số nguyên)
4. gender: Giới tính, phải bằng tiếng Anh: "male" hoặc "female"
5. mbti: Loại MBTI (ví dụ: INTJ, ENFP, v.v.)
6. country: Quốc gia (sử dụng tiếng Trung, ví dụ: "中国")
7. profession: Nghề nghiệp
8. interested_topics: Mảng các chủ đề quan tâm

Quan trọng:
- Tất cả giá trị trường phải là chuỗi hoặc số; không sử dụng ký tự xuống dòng
- persona phải là một đoạn văn bản mạch lạc
- Sử dụng tiếng Trung (trừ trường gender, phải bằng tiếng Anh: male/female)
- Nội dung phải nhất quán với thông tin thực thể
- age phải là số nguyên hợp lệ; gender phải là "male" hoặc "female"
"""

PROFILE_GROUP_USER_PROMPT_TEMPLATE = """\
Tạo hồ sơ tài khoản mạng xã hội chi tiết cho thực thể tổ chức/nhóm, khôi phục tối đa tình hình thực tế đã biết.

Tên Thực thể: {entity_name}
Loại Thực thể: {entity_type}
Tóm tắt Thực thể: {entity_summary}
Thuộc tính Thực thể: {attrs_str}

Thông tin Bối cảnh:
{context_str}

Vui lòng tạo JSON với các trường sau:

1. bio: Tiểu sử tài khoản chính thức, 200 ký tự, chuyên nghiệp và phù hợp
2. persona: Mô tả hồ sơ tài khoản chi tiết (văn bản thuần 2000 ký tự), bao gồm:
   - Thông tin cơ bản tổ chức (tên chính thức, loại tổ chức, bối cảnh thành lập, chức năng chính)
   - Định vị tài khoản (loại tài khoản, đối tượng mục tiêu, chức năng cốt lõi)
   - Phong cách giao tiếp (đặc điểm ngôn ngữ, cách diễn đạt phổ biến, chủ đề cấm kỵ)
   - Đặc điểm nội dung (loại nội dung, tần suất đăng bài, khoảng thời gian hoạt động)
   - Lập trường và thái độ (vị trí chính thức về chủ đề cốt lõi, cách xử lý tranh cãi)
   - Ghi chú đặc biệt (hồ sơ nhóm đại diện, thói quen vận hành)
   - Ký ức tổ chức (phần quan trọng của hồ sơ tổ chức; mô tả mối liên hệ của tổ chức với sự kiện, và các hành động và phản ứng hiện có trong sự kiện)
3. age: Cố định là 30 (tuổi ảo cho tài khoản tổ chức)
4. gender: Cố định là "other" (tài khoản tổ chức sử dụng "other" để chỉ không phải cá nhân)
5. mbti: Loại MBTI, dùng để mô tả phong cách tài khoản, ví dụ: ISTJ cho phong cách nghiêm ngặt và bảo thủ
6. country: Quốc gia (sử dụng tiếng Trung, ví dụ: "中国")
7. profession: Mô tả chức năng tổ chức
8. interested_topics: Mảng các lĩnh vực quan tâm

Quan trọng:
- Tất cả giá trị trường phải là chuỗi hoặc số; không cho phép giá trị null
- persona phải là một đoạn văn bản mạch lạc; không sử dụng ký tự xuống dòng
- Sử dụng tiếng Trung (trừ trường gender, phải bằng tiếng Anh: "other")
- age phải là số nguyên 30; gender phải là chuỗi "other"
- Giao tiếp tài khoản tổ chức phải phù hợp với danh tính và định vị của họ"""

# ═══════════════════════════════════════════════════════════════
# zep_tools.py
# ═══════════════════════════════════════════════════════════════

SUB_QUESTION_SYSTEM_PROMPT = """\
Bạn là chuyên gia phân tích câu hỏi chuyên nghiệp. Nhiệm vụ của bạn là phân tách một câu hỏi phức tạp thành nhiều câu hỏi phụ có thể được quan sát độc lập trong thế giới mô phỏng.

Yêu cầu:
1. Mỗi câu hỏi phụ nên đủ cụ thể để tìm các hành vi hoặc sự kiện liên quan của Agent trong thế giới mô phỏng
2. Các câu hỏi phụ nên bao phủ các chiều khác nhau của câu hỏi gốc (ví dụ: ai, cái gì, tại sao, như thế nào, khi nào, ở đâu)
3. Các câu hỏi phụ nên liên quan đến kịch bản mô phỏng
4. Trả về định dạng JSON: {"sub_queries": ["câu hỏi phụ 1", "câu hỏi phụ 2", ...]}"""

SUB_QUESTION_USER_PROMPT_TEMPLATE = """\
Bối cảnh yêu cầu mô phỏng:
{requirement}

{context}

Vui lòng phân tách câu hỏi sau thành {max_queries} câu hỏi phụ:
{query}

Trả về danh sách câu hỏi phụ theo định dạng JSON."""

SUB_QUESTION_FALLBACK_TEMPLATES = [
    "{query}",
    "Các bên tham gia chính của {query}",
    "Nguyên nhân và tác động của {query}",
    "Quá trình phát triển của {query}",
]

INTERVIEW_PROMPT_PREFIX = (
    "Bạn đang được phỏng vấn. Vui lòng dựa vào hồ sơ cá nhân, tất cả ký ức và hành động trong quá khứ "
    "để trả lời các câu hỏi sau trực tiếp bằng văn bản thuần.\n"
    "Yêu cầu phản hồi:\n"
    "1. Trả lời trực tiếp bằng ngôn ngữ tự nhiên; không gọi bất kỳ công cụ nào\n"
    "2. Không trả về định dạng JSON hoặc định dạng gọi công cụ\n"
    "3. Không sử dụng tiêu đề Markdown (ví dụ: #, ##, ###)\n"
    "4. Trả lời lần lượt từng câu hỏi, bắt đầu mỗi câu trả lời bằng 'Câu hỏi X:' (X là số thứ tự câu hỏi)\n"
    "5. Phân tách mỗi câu trả lời bằng một dòng trống\n"
    "6. Mỗi câu trả lời nên có nội dung thực chất — ít nhất 2-3 câu cho mỗi câu hỏi\n\n"
)

INTERVIEW_SELECT_SYSTEM_PROMPT = """\
Bạn là chuyên gia lập kế hoạch phỏng vấn chuyên nghiệp. Nhiệm vụ của bạn là chọn đối tượng phỏng vấn phù hợp nhất từ danh sách các Agent mô phỏng dựa trên yêu cầu phỏng vấn.

Tiêu chí lựa chọn:
1. Danh tính/nghề nghiệp của Agent liên quan đến chủ đề phỏng vấn
2. Agent có thể nắm giữ quan điểm độc đáo hoặc có giá trị
3. Chọn các góc nhìn đa dạng (ví dụ: người ủng hộ, người phản đối, bên trung lập, chuyên gia, v.v.)
4. Ưu tiên các vai trò liên quan trực tiếp đến sự kiện

Trả về định dạng JSON:
{
    "selected_indices": [danh sách chỉ số Agent được chọn],
    "reasoning": "Giải thích lý do lựa chọn"
}"""

INTERVIEW_SELECT_USER_PROMPT_TEMPLATE = """\
Yêu cầu phỏng vấn:
{interview_requirement}

Bối cảnh mô phỏng:
{simulation_requirement}

Danh sách Agent khả dụng (tổng cộng {agent_count}):
{agent_summaries_json}

Vui lòng chọn tối đa {max_agents} Agent phù hợp nhất cho phỏng vấn và giải thích lý do lựa chọn."""

INTERVIEW_QUESTION_SYSTEM_PROMPT = """\
Bạn là nhà báo/người phỏng vấn chuyên nghiệp. Tạo 3-5 câu hỏi phỏng vấn chuyên sâu dựa trên yêu cầu phỏng vấn.

Yêu cầu câu hỏi:
1. Câu hỏi mở khuyến khích câu trả lời chi tiết
2. Câu hỏi mà các vai trò khác nhau có thể trả lời khác nhau
3. Bao phủ nhiều chiều bao gồm sự kiện, ý kiến và cảm xúc
4. Ngôn ngữ tự nhiên, như một cuộc phỏng vấn thực
5. Giữ mỗi câu hỏi dưới 50 ký tự; ngắn gọn và rõ ràng
6. Hỏi trực tiếp; không bao gồm mô tả bối cảnh hoặc tiền tố

Trả về định dạng JSON: {"questions": ["câu hỏi 1", "câu hỏi 2", ...]}"""

INTERVIEW_QUESTION_USER_PROMPT_TEMPLATE = """\
Yêu cầu phỏng vấn: {interview_requirement}

Bối cảnh mô phỏng: {simulation_requirement}

Vai trò người được phỏng vấn: {agent_roles}

Vui lòng tạo 3-5 câu hỏi phỏng vấn."""

INTERVIEW_QUESTION_FALLBACK_TEMPLATES = [
    "Về {interview_requirement}, quan điểm của bạn là gì?",
    "Vấn đề này ảnh hưởng như thế nào đến bạn hoặc nhóm bạn đại diện?",
    "Bạn nghĩ vấn đề này nên được giải quyết hoặc cải thiện như thế nào?",
]

INTERVIEW_QUESTION_DEFAULT_TEMPLATE = "Về {interview_requirement}, bạn có suy nghĩ gì?"

INTERVIEW_SUMMARY_SYSTEM_PROMPT = """\
Bạn là biên tập viên tin tức chuyên nghiệp. Dựa trên phản hồi từ nhiều người được phỏng vấn, tạo bản tóm tắt phỏng vấn.

Yêu cầu tóm tắt:
1. Trích xuất quan điểm chính của mỗi bên
2. Xác định các điểm đồng thuận và bất đồng
3. Đánh dấu các trích dẫn có giá trị
4. Giữ khách quan và trung lập; không thiên vị bất kỳ bên nào
5. Giữ trong phạm vi 1000 ký tự

Ràng buộc định dạng (phải tuân thủ):
- Sử dụng các đoạn văn bản thuần phân tách bằng dòng trống
- Không sử dụng tiêu đề Markdown (ví dụ: #, ##, ###)
- Không sử dụng đường phân cách (ví dụ: ---, ***)
- Khi trích dẫn lời gốc của người được phỏng vấn, sử dụng dấu ngoặc kép
- **In đậm** có thể được sử dụng để đánh dấu từ khóa, nhưng không sử dụng cú pháp Markdown khác"""

INTERVIEW_SUMMARY_USER_PROMPT_TEMPLATE = """\
Chủ đề phỏng vấn: {interview_requirement}

Nội dung phỏng vấn:
{interview_texts}

Vui lòng tạo bản tóm tắt phỏng vấn."""

# ═══════════════════════════════════════════════════════════════
# simulation.py (API)
# ═══════════════════════════════════════════════════════════════

API_INTERVIEW_PROMPT_PREFIX = (
    "Dựa vào hồ sơ cá nhân, tất cả ký ức và hành động trong quá khứ, "
    "trả lời trực tiếp bằng văn bản mà không gọi bất kỳ công cụ nào: "
)
