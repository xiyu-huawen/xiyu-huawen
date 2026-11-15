"""Generate Document 4: 锡语华纹_源代码复现与运行指南.docx"""
import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.doc_builder_helper import DocxBuilder

def build_source_reproduction_guide():
    builder = DocxBuilder()
    builder.set_header_footer("锡语华纹 · 源代码复现与运行指南 (Release 1.3.0)")

    # Title Block
    builder.add_title_block(
        title="锡 语 华 纹",
        subtitle="源代码复现与运行指南\n专为赛事评审委员会与技术裁判制定的全环境复现与代码审计指引",
        meta_dict={
            "参赛项目名称": "锡语华纹：传统纹样基因库与现代器物共创平台",
            "当前交付版本": "Release 1.3.0 (定稿交付版)",
            "核心运行模式": "模式A: Docker 容器化全栈复现 / 模式B: 本地物理机源码分端运行 / 模式C: 预构建镜像极速运行",
            "关键依赖特性": "100% 离线自足闭环 · 零外部大模型依赖 · 确定性几何布尔算子引擎",
            "必须底层依赖": "Docker 24+ 或 Python 3.11+ / libcairo2 / Node.js 18+ / npm 9+",
            "文档制定日期": "2026年11月",
            "文档面向对象": "大赛技术评审专家、系统裁判、开源审计人员、高校科研评测组"
        }
    )

    # Executive Callout
    builder.add_callout(
        "【致赛事评审专家】尊敬的评审委员会专家与技术裁判：\n"
        "为了让赛事方能够以最严谨、最透明、最便捷的方式对「锡语华纹」项目的源代码进行编译、运行、功能复核与技术审计，"
        "本指南详细阐明了系统运行所需的【必须依赖】与【可选扩展】，并提供了完整的 Docker 源码一键构建以及本地物理机分端运行方案。\n"
        "【核心定调】：本项目的所有核心业务（知识库考据、3D纹样星球、造物剧场、24参数比选、12类3D器型、活态共创工坊、工艺透视器毫米测距、DFM承力焊点分析、1:1毫米DXF工程包导出），"
        "均由本地自研的确定性计算几何算法（Shapely + ezdxf）和 WebGL/Three.js 数学网格实时驱动，绝对不需要任何外部大模型或联网 API Key 即可 100% 完整闭环运行！",
        title="【赛事复现总则与核心承诺】",
        border_color="1A2A3A",
        bg_color="F0F4F8"
    )

    # Section 1
    builder.add_heading_1("第一章 赛事复现总览与依赖环境清单")

    builder.add_heading_2("1.1 必须的基础运行依赖（按运行模式区分）")
    builder.add_paragraph(
        "评审专家可根据现场测试环境或评测机配置，在以下两种基础运行模式中任选一种："
    )

    dep_table = [
        ["运行模式", "适用场景", "必须安装的软件与系统依赖", "推荐硬件与网络配置"],
        ["模式 A\n(强烈推荐)\nDocker 全栈复现", "评审快速验证、比赛现场评测、免污染宿主机环境。", "• Docker Engine 24.0+ 或 Docker Desktop 4.20+\n• Docker Compose v2 (支持 docker compose 命令)\n• 支持 macOS (Apple Silicon), Linux x86_64, Windows WSL2", "• CPU 2核及以上\n• 内存 >= 4 GB (推荐 8 GB)\n• 磁盘空间 >= 10 GB\n• 宿主机端口 8088 (可自定义)"],
        ["模式 B\n本地源码分端运行", "深度代码审计、单元测试执行、代码断点调试与二次开发。", "• 后端：Python 3.11+，系统级底层库 libcairo2\n• 前端：Node.js 18.0+ / 20.0+ (LTS)，npm 9.0+\n• 系统包管理器：apt / brew / yum", "• 具备完整的本地编译工具链\n• 支持 WebGL 的现代浏览器\n• 后端端口 8000，前端端口 5173"]
    ]
    builder.add_table(dep_table[0], dep_table[1:], col_widths=[1.5, 1.4, 1.8, 1.3])

    builder.add_heading_2("1.2 关键说明：大模型及外部 AI 依赖的边界（非必须，零强依赖）")
    builder.add_callout(
        "【大模型依赖情况严正声明】\n"
        "赛事方在评测时往往高度关注系统是否对外部昂贵的云端大模型存在强依赖。我们郑重声明：\n"
        "1. 零强依赖：本平台的核心价值在于「可溯源的文化基因库 + 因器而变的几何布尔算子 + 1:1 DXF 闭合工程包」，所有核心算法均在本地运行，完全不需要大模型！\n"
        "2. 解耦插件：外部 AI 仅作为非核心的松耦合插件设计：\n"
        "   - 自然语言意图召回模糊分词（可选 OpenAI 兼容接口）：未配置时使用本地内置的高精度同义词与白名单映射规则，功能完全等效；\n"
        "   - 东方实境棚拍参考图（可选即梦 AI 或 OpenAI Edits 接口）：未配置时前端诚实提示未配置，绝不导致系统错误，矢量与工程包导出功能 100% 正常；\n"
        "3. 纯内网可用：评委拔掉网线，系统全要素功能依然流畅自如！",
        title="【大模型与外部依赖边界声明】",
        border_color="C5A059",
        bg_color="FDFBF7"
    )

    # Section 2
    builder.add_heading_1("第二章 模式一：Docker Compose 源码构建运行（赛事方首选）")
    builder.add_paragraph(
        "通过标准的 Docker Compose 源码构建，可一次性编译前后端镜像并启动，彻底隔绝宿主机系统环境差异："
    )

    builder.add_heading_2("2.1 步骤一：初始化环境配置文件（.env）")
    builder.add_paragraph("在项目根目录下复制一份标准环境变量配置文件：")
    builder.add_code_block("cp .env.example .env")
    builder.add_paragraph("编辑 `.env` 文件，确认或修改以下关键配置项：")
    builder.add_code_block(
        "# 设置后台管理密码（用于打样管理与数据导入）\n"
        "ADMIN_PASSWORD=judge-secure-pass-2026\n\n"
        "# 设置对外映射端口（默认为 8088；若本机 8088 冲突，可修改为 8098 或其他可用端口）\n"
        "PORT=8088\n\n"
        "# 设置构建镜像架构（ARM64 填写 1.3.0-arm64，x86_64 填写 1.3.0-amd64）\n"
        "IMAGE_TAG=1.3.0-arm64"
    )

    builder.add_heading_2("2.2 步骤二：源码一键构建并启动服务")
    builder.add_paragraph("执行标准构建与拉起命令：")
    builder.add_code_block("docker compose up -d --build")
    builder.add_paragraph(
        "Docker 将自动读取 deploy/backend.Dockerfile 与 deploy/frontend.Dockerfile，完成底层依赖安装与前端 Vite 生产构建，"
        "并自动挂载独立的命名持久卷 xiyu-data。"
    )

    builder.add_heading_2("2.3 步骤三：服务健康检查")
    builder.add_paragraph("在终端中执行健康检查探测：")
    builder.add_code_block("curl http://localhost:8088/api/health")
    builder.add_paragraph("当控制台输出预期 JSON：{\"status\":\"ok\",\"patterns\":60} 时，表明服务已完全就绪！")

    builder.add_heading_2("2.4 步骤四：在浏览器中打开全系统")
    builder.add_paragraph("打开 Chrome、Edge、Safari 或 Firefox 浏览器，访问：")
    builder.add_code_block("http://localhost:8088")
    builder.add_paragraph("即可进入「锡语华纹」展陈式首页进行全要素功能测试。")

    builder.add_picture_with_caption(
        str(ROOT / "docs/previews/home-desktop.png"),
        "图 2-1 源码构建成功后浏览器呈现的系统全景首页"
    )

    # Section 3
    builder.add_heading_1("第三章 模式二：本地物理机源码分端运行（深度代码审计）")

    builder.add_heading_2("3.1 后端环境搭建与运行（FastAPI + Python 3.11）")
    builder.add_numbered("1.", "安装系统级底层图形库 libcairo2（必须依赖，用于 Cairo 矢量光栅化与 PNG 输出）：", bold_prefix="系统底层库：")
    builder.add_code_block(
        "# Debian / Ubuntu 系列 Linux:\n"
        "sudo apt-get update && sudo apt-get install -y libcairo2 libcairo2-dev\n\n"
        "# macOS (通过 Homebrew 安装):\n"
        "brew install cairo\n\n"
        "# CentOS / RHEL 系列 Linux:\n"
        "sudo yum install -y cairo cairo-devel"
    )
    builder.add_numbered("2.", "创建并激活 Python 3.11+ 独立虚拟环境：", bold_prefix="创建虚拟环境：")
    builder.add_code_block(
        "python3 -m venv .venv\n"
        "source .venv/bin/activate  # Windows 用户执行: .venv\\Scripts\\activate"
    )
    builder.add_numbered("3.", "按锁定依赖文件精确安装 Python 依赖包：", bold_prefix="安装 Python 依赖：")
    builder.add_code_block("pip install -r backend/requirements.lock")
    builder.add_numbered("4.", "配置临时环境变量并启动 FastAPI 异步后端服务：", bold_prefix="启动后端服务：")
    builder.add_code_block(
        "export DATA_DIR=\"./runtime\"\n"
        "export ADMIN_PASSWORD=\"judge-secure-pass-2026\"\n"
        "uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload"
    )
    builder.add_paragraph("启动后，评审人员可访问 http://localhost:8000/docs 查看完整的 Swagger 交互式 API 文档。")

    builder.add_heading_2("3.2 前端环境搭建与运行（Vue 3 + Vite）")
    builder.add_numbered("1.", "进入前端工程根目录：", bold_prefix="进入前端：")
    builder.add_code_block("cd frontend")
    builder.add_numbered("2.", "安装锁定版本的前端 npm 依赖：", bold_prefix="安装依赖：")
    builder.add_code_block("npm ci")
    builder.add_numbered("3.", "启动 Vite 本地开发调试服务器：", bold_prefix="启动开发服务：")
    builder.add_code_block("npm run dev")
    builder.add_paragraph("Vite 将启动并在终端输出访问地址（如 http://localhost:5173），其内置代理会自动将 /api 与 /assets 请求转发至后端 8000 端口。")
    builder.add_numbered("4.", "前端生产构建与类型合规校验：", bold_prefix="编译校验：")
    builder.add_code_block("npm run build")
    builder.add_paragraph("当输出 dist/ 静态产物无报错时，证实前端 TypeScript 类型定义与 Vue 3 模板 100% 严谨合规。")

    builder.add_heading_2("3.3 原始学术资料全量解析流水线验证（可选）")
    builder.add_paragraph(
        "如需核验系统如何从 60 篇原始 Word 文档提取文化基因，可在项目根目录下执行全量 Ingest 解析指令："
    )
    builder.add_code_block("python -m backend.ingest 原始内容/数据 seed")
    builder.add_paragraph(
        "系统将自动解析每篇文档的表格与高清图像，提取 M/C/S 基因，生成标准矢量 SVG 与 seed/catalog.json 数据字典。"
    )

    # Section 4
    builder.add_heading_1("第四章 模式三：预构建镜像极速免编译复现（评委极速通道）")
    builder.add_paragraph(
        "若评审专家时间紧迫或评测机无法连接公网下载包，可直接利用 outputs/1.3.0/ 目录中预先打包的双架构 Docker 镜像，实现两分钟免编译极速拉起："
    )
    builder.add_code_block(
        "# 1. 加载对应架构的离线镜像包\n"
        "# 若为 ARM64 机器 (Apple Silicon Mac / ARM64 Linux):\n"
        "docker load -i outputs/1.3.0/xiyuhuawen-1.3.0-arm64.tar.gz\n"
        "# 若为 x86_64 / AMD64 机器:\n"
        "docker load -i outputs/1.3.0/xiyuhuawen-1.3.0-amd64.tar.gz\n\n"
        "# 2. 复制环境配置\n"
        "cp .env.example .env\n\n"
        "# 3. 免构建直接启动\n"
        "docker compose up -d --no-build\n\n"
        "# 4. 访问系统: http://localhost:8088"
    )

    # Section 5
    builder.add_heading_1("第五章 赛事方核心功能全要素验证清单（Checklist）")
    builder.add_paragraph("赛事裁判可对照以下八大测试动线逐一验证系统功能与产出物质量：")

    checklist_data = [
        ["序号", "功能模块", "实操测试动作", "预期技术效果与判定准则"],
        ["01", "展陈首页与检索", "打开首页，在检索栏输入“莲心”或“安宁”进行模糊查询。", "即时筛选出匹配卡片，清晰呈现朝代、母体载体、缩略图与文化标签。"],
        ["02", "纹样星球 3D 图谱", "切入「纹样星球」，拖动三维天体旋转，松开观察；点击任意节点。", "拖拽时阻尼暂停，松开 1.5 秒后平滑恢复自转；节点高亮连线与溯源卡片。"],
        ["03", "纹样书房权威文献", "进入「纹样书房」，浏览文章底部「学术出处与机构链接」。", "完整呈现威海市文旅局、故宫博物院、UNESCO 等 13 条官方权威外链。"],
        ["04", "造物剧场五阶段", "进入「造物剧场」，经历定意、探源、比较、共创、成器全流程。", "基于 24 参数矩阵在毫秒级内输出三向最优方案；文化核心图元锁定锚点。"],
        ["05", "因器而变 3D 换器", "在器物视图中切换茶承、紫砂壶、笔筒、香插等器型；切换金属饰面。", "同一纹样在平曲面间无损贴合；素锡/亮锡/暖金金属光泽与微浮雕真实呈现。"],
        ["06", "活态共创工坊", "进入「工坊」，载入器物纹样作为底稿，开启“4向对称”自由绘制。", "笔画对称实时绽放；入库生成唯一 UUID，标记为当代资产并生成演进树。"],
        ["07", "工艺透视器与 DFM", "在成器页面展开透视器，拖动双端标尺；点击“DFM 拓扑扫描”。", "标尺精确显示毫米读数；算法自动扫描最细线宽并标定 4 处承力焊接点。"],
        ["08", "1:1 DXF 工程包交付", "点击「下载工程包」，解压查看 parameters.json 与 1to1-mm.dxf。", "在 CAD 中打开 DXF，验证 OUTLINE 与 HOLES 多段线绝对闭合且为 1:1 毫米刻度。"]
    ]
    builder.add_table(checklist_data[0], checklist_data[1:], col_widths=[0.6, 1.3, 2.1, 2.0])

    builder.add_picture_with_caption(
        str(ROOT / "docs/previews/theatre-production-create.png"),
        "图 5-1 造物剧场五阶段流程与十二器型三维曲面贴附核验实景"
    )

    # Section 6
    builder.add_heading_1("第六章 自动化测试套件执行实录")
    builder.add_paragraph(
        "系统内置了完整的自动化单元测试与端到端集成测试，赛事裁判可随时在本地执行验证："
    )
    builder.add_heading_2("6.1 后端 27 项自动化测试执行（pytest）")
    builder.add_paragraph("在虚拟环境中运行：")
    builder.add_code_block("python -m pytest tests -q")
    builder.add_paragraph(
        "终端将输出 27 passed in xx.xxs (100% 成功率)，全面覆盖了 60 篇文献解析、布尔几何算子、1:1 DXF 生成、SafeET 注入拦截及当代资产继承等所有硬核功能点。"
    )

    builder.add_heading_2("6.2 双架构 20 项镜像端到端测试")
    builder.add_paragraph("在具备 Docker 环境的终端中可重新执行自动化镜像回归脚本：")
    builder.add_code_block("python scripts/acceptance.py arm64 8098")
    builder.add_paragraph("脚本将全自动验证冷启动、静态资产、SVG/PNG 导出、容器重启持久化与独立数据卷灾难恢复。")

    # Section 7
    builder.add_heading_1("第七章 常见问题排查与技术支持（FAQ）")

    faqs = [
        ("Q1：Docker 提示端口 8088 冲突已被占用？",
         "解决方案：编辑 .env 文件，将 PORT 改为 8098 或其他可用端口（如 PORT=8098），随后重新执行 docker compose up -d 即可。"),
        ("Q2：本地运行 Python 后端提示 ImportError: cannot load library 'libcairo.so.2'？",
         "原因分析：系统缺少 libcairo2 底层动态链接库。\n"
         "解决方案：Linux 执行 sudo apt-get install -y libcairo2；macOS 执行 brew install cairo；Windows 推荐直接使用 Docker 容器模式运行。"),
        ("Q3：如何彻底停止服务并释放资源？",
         "日常停止服务执行 docker compose stop；彻底销毁容器执行 docker compose down；如需清空持久化测试数据执行 docker compose down -v。"),
        ("Q4：未配置大模型 API Key 是否会弹出报错或不可用？",
         "绝不会！未配置大模型密钥时，系统仅在点击“AI棚拍意境图”时诚实显示未配置提示，所有结构设计、3D交互、共创工坊与 1:1 DXF 导出均 100% 正常运行。")
    ]
    for q, a in faqs:
        builder.add_heading_2(q)
        builder.add_paragraph(a)

    out_path = ROOT / "docs" / "锡语华纹_源代码复现与运行指南.docx"
    builder.save(str(out_path))

if __name__ == "__main__":
    build_source_reproduction_guide()
