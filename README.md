# 每日英文阅读练习

给孩子（11岁，深圳公立六年级水平）生成每天约10分钟的英文阅读练习包，会根据家长反馈自动调整第二天难度。

## 结构

- `profile.json`：孩子档案 + 当前难度状态（由入学测试确定初始值，之后由反馈自动调整）
- `prompts/daily_reading.md`：生成当天内容包的 prompt
- `prompts/english_review.md`：独立于生成流程的英语审校 prompt，专门挑改故事/例句/题目里不自然或不正确的英语
- `enrich_content.py`：补充发音音频（story-YYYY-MM-DD.mp3 / word-YYYY-MM-DD-N.mp3）和生词音标
- `generate_html.py`：把当天生成的 `day-YYYY-MM-DD.json` 转成网页
- `validate_reading.py`：检查生成内容是否完整；`--json-only` 只查 JSON（生成后先跑一次，音频/网页生成前拦掉明显问题），不带参数时还会检查网页文件是否存在，作为发布前的最后一道关卡；生词表覆盖度检查不通过会直接判失败
- `update_profile_from_feedback.py`：根据家长反馈标签调整 profile.json
- `mark_word_known.py`：把家长标记为"已认识"的生词写入 profile.json
- `publish.sh`：更新 latest / 归档当天的 html+json+音频 / 更新首页 / commit + push
- `.github/workflows/daily-reading.yml`：手动触发生成当天内容包并发布
- `.github/workflows/handle-feedback.yml`：家长在网页上点反馈按钮 → 创建 GitHub Issue → 自动调整难度并关闭 Issue
- `.github/workflows/handle-known-word.yml`：家长在网页上点某个生词的"已认识" → 创建 GitHub Issue → 写入 profile.json 并关闭 Issue

## 每天怎么用

1. 手动触发 `Daily Kids Reading` workflow（Actions 标签页 → Run workflow），或以后接入定时触发
2. 打开 GitHub Pages 首页，做当天的练习
3. 做完在页面底部选一个反馈标签，点击后会跳到 GitHub 新建 Issue 页面，内容已预填好，直接提交
4. 系统自动读取反馈，调整明天的难度

内容方向（故事风格、题目细节等）还在持续调整中，见对话记录。
