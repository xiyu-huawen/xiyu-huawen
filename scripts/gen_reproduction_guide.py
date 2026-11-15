"""Generate Document 2: 锡语华纹_系统交付与镜像复现评审手册.docx"""
import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.doc_builder_helper import DocxBuilder

def build_reproduction_guide():
    builder = DocxBuilder()
    builder.set_header_footer("锡语华纹 · 系统交付与镜像复现评审手册 (Release 1.3.0)")

    # Title Block
    builder.add_title_block(
        title="锡 语 华 纹",
        subtitle="系统交付与镜像复现评审手册\n专为评审专家与技术裁判制定的 Docker 容器化一键部署与全链路复现规范",
        meta_dict={
            "交付系统全称": "锡语华纹：传统纹样基因库与现代器物共创平台",
            "当前交付版本": "Release 1.3.0 (定稿交付版)",
            "镜像交付包目录": "outputs/1.3.0/ (含ARM64与AMD64双架构镜像)",
            "核心复现目标": "拔掉网线完全离线可跑 · 3步极速启动 · 7大功能路径全要素验证",
            "支持运行平台": "Apple Silicon (M1/M2/M3/M4) / 通用 Linux x86_64 (AMD64) / 云服务器",
            "文档制定日期": "2026年11月",
            "文档面向对象": "大赛评审专家、技术裁判、工坊协同工程师、开源评测人员"
        }
    )

    # Executive Callout
    builder.add_callout(
        "【评委复现致辞】尊敬的评审专家：为了让您能够以最高效、最客观、最严谨的方式检验「锡语华纹」项目的技术真实性与工程完成度，"
        "我们坚持「代码不造假、运行全离线、镜像一键起、数据可复原」的交付标准。"
        "本交付包（outputs/1.3.0）内已完整封装系统的前端编译静态包、后端FastAPI服务、Shapely几何拓扑算子引擎、Three.js三维程序化模型、"
        "60篇学术考据纹样全量元数据以及145份矢量图元资产。"
        "您无需配置复杂的Python环境、Node.js依赖或安装编译依赖包，只需在支持Docker的终端中执行三条标准命令，"
        "即可在本地计算机上100%无损复现整个平台的所有功能。本手册将为您提供极其详尽的单步实操指引与验证核对指标。",
        title="【致评审裁判专家】",
        border_color="1A2A3A",
        bg_color="F0F4F8"
    )

    # Section 1
    builder.add_heading_1("第一章 交付工件清单与哈希完整性校验")

    builder.add_heading_2("1.1 交付工件清单目录（outputs/1.3.0/）")
    builder.add_paragraph(
        "所有定稿交付的核心工件均统一归档在项目根目录的 outputs/1.3.0/ 路径下，文件清单如下："
    )

    pkg_table = [
        ["文件名", "文件大小", "文件属性与格式", "主要作用与说明"],
        ["xiyuhuawen-1.3.0-arm64.tar.gz", "528 MB", "Docker 镜像归档 (ARM64)", "专用于 Apple Silicon Mac (M系列芯片) 及 ARM64 架构 Linux 服务器的一键部署镜像。"],
        ["xiyuhuawen-1.3.0-amd64.tar.gz", "534 MB", "Docker 镜像归档 (AMD64)", "专用于通用 Intel / AMD x86_64 架构 Linux / Windows 服务器的一键部署镜像。"],
        ["xiyuhuawen-source-1.3.0.tar.gz", "287 MB", "全套源代码与依赖归档", "包含全套 Vue 3 前端源码、FastAPI 后端源码、seed 种子资料及构建配置文件。"],
        ["底稿设计工程包.zip", "2.6 MB", "实际运行导出的工程包样件", "内含真实 1:1 毫米制 DXF 轮廓文件、SVG 矢量、参数规范及文化溯源 JSON。"],
        ["当代原作-锡光续纹.svg", "1.0 MB", "工坊实测导出的当代矢量原图", "实测通过工坊绘制并入库的当代活态纹样资产，包含 nonzero 复合金属轮廓。"],
        ["当代资产档案-锡光续纹.json", "2.0 MB", "当代资产谱系元数据快照", "记录该作品的唯一 UUID、父底稿编号、可编辑笔画配方及引用的权威文献快照。"],
        ["SHA256SUMS", "664 B", "文本哈希校验清单", "记录上述所有交付文件的安全 SHA256 哈希值，用于防篡改校验。"]
    ]
    builder.add_table(pkg_table[0], pkg_table[1:], col_widths=[1.8, 0.8, 1.2, 2.2])

    builder.add_heading_2("1.2 SHA256 完整性哈希对照表")
    builder.add_paragraph("评委在部署前可使用标准终端工具校验所有文件的 SHA256 指纹，确保交付文件绝对完整未受篡改：")

    hash_data = [
        ["交付工件名称", "标准 SHA256 完整性校验哈希值 (SHA-256 Checksum)"],
        ["xiyuhuawen-1.3.0-arm64.tar.gz", "140f307fd64a2f8f0d8c9d69b1436f61b845740279c01c75fb9bed40195e7eb1"],
        ["xiyuhuawen-1.3.0-amd64.tar.gz", "4ce9702362c0f75bb6c1098c08a090af3effa0f4ffc8c42add28a0c27545f891"],
        ["xiyuhuawen-source-1.3.0.tar.gz", "f02bd1e1daa7be48bf86f5ff36a72ea4370c5ed5257f9a16f6f9beeb4ad0d0cf"],
        ["底稿设计工程包.zip", "dba3a0624c140cd317dc744f99e684b91f576b77f332685778729ea5cb953324"],
        ["当代资产档案-锡光续纹.json", "df71e4bf8cefcd85f389998b43cce185ddebeecb09dfe5a128d3bdb6f1aa70f1"],
        ["当代原作-锡光续纹.svg", "73eeb26f083fde3f2c81fdc80731a4221183bf79b2fed872e9b020eee1184ebf"]
    ]
    builder.add_table(hash_data[0], hash_data[1:], col_widths=[2.2, 3.8])

    builder.add_paragraph("在 Mac 或 Linux 终端中执行以下命令即可全自动比对：", bold_prefix="校验命令：")
    builder.add_code_block("shasum -a 256 -c outputs/1.3.0/SHA256SUMS")

    # Section 2
    builder.add_heading_1("第二章 评审软硬件环境规范与架构配置")

    builder.add_heading_2("2.1 推荐硬件与系统环境")
    builder.add_bullet("处理器架构：支持 Apple Silicon (ARM64) 或 Intel / AMD 64位处理器 (x86_64)。", bold_prefix="CPU：")
    builder.add_bullet("内存建议：物理内存 >= 4 GB (推荐 8 GB 以上)，磁盘剩余可用空间 >= 10 GB。", bold_prefix="内存与存储：")
    builder.add_bullet("操作系统：macOS 12+ / Ubuntu 20.04+ / CentOS 8+ / Debian 11+ / Windows 11 (WSL2)。", bold_prefix="OS：")
    builder.add_bullet("容器引擎：Docker Desktop 4.20+ 或 Docker Engine 24.0+，且支持 Docker Compose v2 (docker compose)。", bold_prefix="Docker：")
    builder.add_bullet("客户端浏览器：推荐使用 Chrome 110+ / Edge 110+ / Safari 16+ / Firefox 110+（需开启 WebGL 硬件加速）。", bold_prefix="浏览器：")

    builder.add_heading_2("2.2 容器与网络端口拓扑架构")
    builder.add_paragraph("系统通过标准的 Docker Compose 编排两个紧密协作的高性能微服务容器：")
    
    ports_data = [
        ["容器服务名", "镜像标签名 (ARM64/AMD64)", "内部端口", "对外暴露端口", "核心职责与健康检查指标"],
        ["web", "xiyuhuawen-web:1.3.0", "80/TCP", "宿主机 8088 端口\n(可在.env中配置)", "Nginx 高性能反向代理，承载前端 Vue3 编译单页、静态素材与字体，配置 CSP 安全头。"],
        ["api", "xiyuhuawen-api:1.3.0", "8000/TCP", "仅容器内部网络互联\n不对外暴露端口", "FastAPI Python 后端，承载几何算子与持久化。健康检查：GET /api/health 返回 HTTP 200。"]
    ]
    builder.add_table(ports_data[0], ports_data[1:], col_widths=[1.0, 1.4, 0.8, 1.2, 1.6])

    builder.add_paragraph(
        "数据持久化由独立的 Docker Named Volume 管理（默认卷名为当前目录前缀加上 xiyu-data，如 xsb_xiyu-data），"
        "容器重启或重构镜像时，SQLite 数据库、用户收藏、Contemporary 当代资产与工坊队列数据永不丢失。"
    )

    # Section 3
    builder.add_heading_1("第三章 评委极速复现与部署实操指南")
    builder.add_paragraph("评委只需在项目根目录下按顺序执行以下四步，耗时约 2 分钟即可完成全系统启动：")

    builder.add_heading_2("3.1 步骤一：加载对应架构的 Docker 镜像")
    builder.add_paragraph("根据您当前评审计算机的 CPU 架构选择一条命令执行：")
    builder.add_bullet("若评委使用的是 Apple Silicon Mac (M1/M2/M3/M4) 或 ARM64 Linux：", bold_prefix="【ARM64 架构】")
    builder.add_code_block("docker load -i outputs/1.3.0/xiyuhuawen-1.3.0-arm64.tar.gz")
    builder.add_bullet("若评委使用的是 Intel/AMD 处理器 PC、标准 Linux 服务器或 Windows WSL2：", bold_prefix="【AMD64 架构】")
    builder.add_code_block("docker load -i outputs/1.3.0/xiyuhuawen-1.3.0-amd64.tar.gz")
    builder.add_paragraph("终端将输出 Loaded image: xiyuhuawen-api:1.3.0-... 与 xiyuhuawen-web:1.3.0-...，表示镜像加载成功。")

    builder.add_heading_2("3.2 步骤二：初始化环境配置文件（.env）")
    builder.add_paragraph("从模板复制一份专属环境配置文件，并设置管理员密码与镜像架构标签：")
    builder.add_code_block(
        "cp .env.example .env\n\n"
        "# 若为 ARM64 机器，确认 .env 中包含：\n"
        "ADMIN_PASSWORD=judge-secure-pass-2026\n"
        "PORT=8088\n"
        "IMAGE_TAG=1.3.0-arm64\n\n"
        "# 若为 AMD64 机器，将 IMAGE_TAG 修改为：\n"
        "IMAGE_TAG=1.3.0-amd64"
    )

    builder.add_heading_2("3.3 步骤三：一键启动容器集群并执行健康检查")
    builder.add_paragraph("执行标准启动指令（使用 --no-build 确保纯镜像运行，绝不重新拉取代码编译）：")
    builder.add_code_block("docker compose up -d --no-build")
    builder.add_paragraph("检查服务健康状态，在终端执行：")
    builder.add_code_block("curl http://localhost:8088/api/health")
    builder.add_paragraph("当终端返回预期 JSON：{\"status\":\"ok\",\"patterns\":60} 时，表明后端 API 拓扑引擎与 60 篇全量知识库已完全就绪！")

    builder.add_heading_2("3.4 步骤四：在浏览器中打开系统体验")
    builder.add_paragraph("打开任意现代浏览器（推荐 Chrome 或 Edge），在地址栏输入：")
    builder.add_code_block("http://localhost:8088")
    builder.add_paragraph("即可直接进入「锡语华纹」宏大的宋韵深墨展陈首页，开始全功能复现检验！")

    builder.add_picture_with_caption(
        str(ROOT / "docs/previews/home-desktop.png"),
        "图 3-1 部署成功后浏览器进入的「锡语华纹」展陈式首页"
    )

    # Section 4
    builder.add_heading_1("第四章 评委全功能验证与复现路径（Step-by-Step）")
    builder.add_paragraph("为协助评审专家全面、高效地核验项目各项技术指标，我们梳理出七条标准验证动线：")

    builder.add_heading_2("4.1 路径一：纹样星球三维知识图谱漫游验证")
    builder.add_numbered("1.", "从顶部导航栏点击进入「纹样星球」模块，观察全库 744 个文化节点组成的三维天体；", bold_prefix="观察自转：")
    builder.add_numbered("2.", "系统默认缓慢自转；用鼠标按住球体拖拽，观察自转是否瞬间平滑暂停；松开鼠标后约 1.5 秒自动恢复环视；", bold_prefix="阻尼交互：")
    builder.add_numbered("3.", "点击其中任意纹样节点（如「PAT-001 客家漏石窗」），观察关联关系连线高亮与右侧详情卡片；", bold_prefix="溯源定位：")
    builder.add_numbered("4.", "点击卡片底部的「入器造物」按钮，验证系统是否成功将该纹样作为基底自动携带至造物剧场。", bold_prefix="流转衔接：")

    builder.add_heading_2("4.2 路径二：纹样书房权威文献与机构出处溯源验证")
    builder.add_numbered("1.", "进入「纹样书房」模块，核对全量收录的 17 篇深度学术文章；", bold_prefix="文献总览：")
    builder.add_numbered("2.", "随机打开《什么是纹样的「文化基因」？》或《四叶莲心：窗内的秩序与清正》等文章；", bold_prefix="内容研读：")
    builder.add_numbered("3.", "滑动至文章底部，检查「学术出处与机构链接」索引卡片，点击威海市文旅局、故宫博物院等外链（联网环境下可跳转原出处），验证学术证据链的真实性；", bold_prefix="机构出处：")
    builder.add_numbered("4.", "在书房中点击「图元逐步阅读」，观察传统四叶莲心纹样如何从一阶方框骨架层层解析到中心花形。", bold_prefix="逐步拆解：")

    builder.add_heading_2("4.3 路径三：造物剧场五阶段共创与 24 候选矩阵比选")
    builder.add_numbered("1.", "进入「造物剧场」，在第一步【定意】选择祝愿「八方安宁」、气质「端正」、受礼人「家人」；", bold_prefix="定意选择：")
    builder.add_numbered("2.", "在第二步【探源】核对 PAT-005 八角外框与八方安宁的已确认映射证据；", bold_prefix="探源核验：")
    builder.add_numbered("3.", "在第三步【比较】查看系统瞬间计算的 24 候选方案，在「守形传意」「跨源相生」「疏朗留白」三个方向各查看一组最优构图，点击选择「跨源相生」；", bold_prefix="三向比选：")
    builder.add_numbered("4.", "在第四步【共创】观察四层图元配置，验证文化核心图元是否处于「锁定锚点」保护状态；尝试手绘一条排列轨迹；", bold_prefix="锚点协同：")
    builder.add_numbered("5.", "在第五步【成器】拖动「平面—入器」过渡滑块，旋转观察三维贴附效果。", bold_prefix="成器验证：")

    builder.add_heading_2("4.4 路径四：十二类程序化三维器型与材质光影切换")
    builder.add_numbered("1.", "在三维器物视图中，点击切换不同的器型（如从「茶承」切换为「紫砂壶」「花器」「笔筒」或「香插」）；", bold_prefix="器型遍历：")
    builder.add_numbered("2.", "验证当前共创的纹样是否在不重置参数的前提下，完美贴附适配到新器皿的表面曲率上；", bold_prefix="无损换器：")
    builder.add_numbered("3.", "点击材质工具栏，切换「素锡沉静」「亮锡如镜」「暖金华美」三种金属饰面，观察 WebGL 着色器光影与微距法线凸起变化。", bold_prefix="金属光影：")

    builder.add_heading_2("4.5 路径五：活态共创工坊绘制与当代资产入库")
    builder.add_numbered("1.", "进入「共创工坊」模块，系统可自动载入刚刚设计的器物纹样作为半透明「创作底稿」；", bold_prefix="底稿载入：")
    builder.add_numbered("2.", "选择画笔工具，开启「4向对称」或「镜像对称」，在画布上绘制一组自定义装饰线条，观察笔画的实时对称镜像绽放；", bold_prefix="对称绘制：")
    builder.add_numbered("3.", "点击「当代资产入库」按钮，填写作品命名（如「评审测试新纹」），勾选使用权确认承诺，点击提交入库；", bold_prefix="资产入库：")
    builder.add_numbered("4.", "进入「社区活态资产」库，核对刚刚提交的作品是否成功展示，并显示其唯一的 UUID、引用底稿编号及学术文献快照。", bold_prefix="谱系核验：")

    builder.add_picture_with_caption(
        str(ROOT / "docs/previews/edition-13-community-desktop.png"),
        "图 4-1 社区当代活态资产库与不可变谱系树界面"
    )

    builder.add_heading_2("4.6 路径六：工艺透视器毫米测距与 DFM 智能分析")
    builder.add_numbered("1.", "在成器页面展开「工艺透视器」，界面将纹样映射至 120×120mm 的精密毫米网格；", bold_prefix="毫米网格：")
    builder.add_numbered("2.", "拖动测距标尺的两端测距点，实测对角线读数是否为数学精确值 169.71mm；", bold_prefix="双端测距：")
    builder.add_numbered("3.", "点击「DFM 工艺拓扑扫描」，检查系统输出的分析报告：闭合轮廓数（Islands）、镂空内孔数（Holes）、虚实镂空比（%）及估算的最细特征线宽（Min Feature mm）；", bold_prefix="DFM 扫描：")
    builder.add_numbered("4.", "观察系统在纹样外骨架的北极、南极、东翼、西翼自动标定的 4 处承力焊点（SP-01 至 SP-04）及非遗大师工艺评级（A/B/C级）。", bold_prefix="焊点标定：")

    builder.add_heading_2("4.7 路径七：工坊级 1:1 DXF 工程包下载与 CAD 坐标读回校验")
    builder.add_numbered("1.", "点击「下载工坊制造工程包」，浏览器将瞬间下载一个名为 <作品编号>-engineering.zip 的压缩包；", bold_prefix="工程包下载：")
    builder.add_numbered("2.", "解压该 ZIP 包，检查其内部结构：包含 1to1-mm.dxf、.svg 矢量、parameters.json、design-and-provenance.json 及交付说明.txt；", bold_prefix="文件结构：")
    builder.add_numbered("3.", "打开 parameters.json，核验 units=\"mm\", scale=\"1:1\"，以及 contours 中的 OUTLINE 与 HOLES 数量；", bold_prefix="参数核对：")
    builder.add_numbered("4.", "在任意 CAD 软件（如 AutoCAD、FreeCAD 或 在线 DXF 查看器）中打开该 DXF 文件，验证所有多段线均为封闭状态（Closed=True），且坐标绝对为 1:1 毫米刻度，完美证明制造交付链路闭环！", bold_prefix="CAD 读回：")

    # Section 5
    builder.add_heading_1("第五章 数据持久化、备份与独立卷恢复验证")
    builder.add_paragraph(
        "为证明系统具备工业级的可靠性与数据安全防护能力，评审专家可亲自测试数据热备份与跨卷无损恢复："
    )

    builder.add_heading_2("5.1 停机热备份操作实录")
    builder.add_paragraph("在终端中执行以下指令，将容器持久卷中的数据完整复制到宿主机本地：")
    builder.add_code_block(
        "# 1. 临时停止 API 容器以确保 SQLite WAL 日志完全落盘\n"
        "docker compose stop api\n\n"
        "# 2. 将容器内 /data 完整复制到宿主机 backup-data 目录\n"
        "docker compose cp api:/data ./backup-data\n\n"
        "# 3. 重启 API 容器，业务恢复正常\n"
        "docker compose start api"
    )
    builder.add_paragraph("检查 backup-data/ 目录，应完整包含 platform.db、catalog.json、assets/ 目录等所有元数据。")

    builder.add_heading_2("5.2 恢复至全新独立卷实录（验证无损迁移）")
    builder.add_paragraph("执行以下指令将备份数据注入一个全新的独立 Compose 项目与数据卷中：")
    builder.add_code_block(
        "# 1. 创建全新测试项目的 API 容器\n"
        "docker compose -p xiyu-restore create api\n\n"
        "# 2. 将备份数据注入新容器的持久卷\n"
        "docker compose -p xiyu-restore cp ./backup-data/. api:/data/\n\n"
        "# 3. 修正文件归属权限为容器安全非 root 用户 (UID 10001)\n"
        "docker compose -p xiyu-restore run --rm --no-deps --user 0 api chown -R 10001:10001 /data\n\n"
        "# 4. 验证数据无损性：查询 SQLite 中之前保存的设计与当代资产数量\n"
        "docker compose -p xiyu-restore run --rm --no-deps api python -c \\\n"
        "  'import sqlite3; c=sqlite3.connect(\"/data/platform.db\"); print(\"已恢复设计记录数:\", c.execute(\"select count(*) from designs\").fetchone()[0])'"
    )
    builder.add_paragraph("终端成功输出对应记录数，证实系统具备零丢失的持久化与灾难恢复能力！")

    # Section 6
    builder.add_heading_1("第六章 自动化测试套件与安全审计结果")

    builder.add_heading_2("6.1 双架构 20 项端到端验收测试矩阵")
    builder.add_paragraph(
        "在 outputs/1.3.0 正式定稿打包前，研发团队编写了严格的 scripts/acceptance.py 自动化验收套件，"
        "分别在 ARM64 原生环境与 AMD64 仿真环境中执行了 20 项严苛的自动化回归测试（详见 logs/ 目录下测试记录）："
    )

    tests_data = [
        ["测试项编号", "测试用例名称与验证内容", "ARM64 测试结果", "AMD64 仿真结果"],
        ["TC-01", "干净数据卷冷启动与 Catalog 初始化 (60 篇文档)", "PASSED (100%)", "PASSED (100%)"],
        ["TC-02", "静态资源码与中文字体 (NotoSerifSC.ttf > 100KB)", "PASSED (100%)", "PASSED (100%)"],
        ["TC-03", "自然语言意图召回与已确认图元白名单校验", "PASSED (100%)", "PASSED (100%)"],
        ["TC-04", "三方向比选生成与 24 候选参数评估矩阵优化", "PASSED (100%)", "PASSED (100%)"],
        ["TC-05", "SVG 物理毫米尺寸生成与 PNG Cairo 渲染输出", "PASSED (100%)", "PASSED (100%)"],
        ["TC-06", "1:1 DXF 制造包构造与 ezdxf 闭合多段线拓扑读回", "PASSED (100%)", "PASSED (100%)"],
        ["TC-07", "作品收藏与 API 容器重启后状态持久化校验", "PASSED (100%)", "PASSED (100%)"],
        ["TC-08", "当代资产提交入库 (origin=contemporary 与 UUID 生成)", "PASSED (100%)", "PASSED (100%)"],
        ["TC-09", "开放手绘笔画线宽膨胀与封闭多面域转换", "PASSED (100%)", "PASSED (100%)"],
        ["TC-10", "SafeET 安全审查：强制拒绝 <script> 与外链实体", "PASSED (100%)", "PASSED (100%)"],
        ["TC-11", "nonzero 与 evenodd 填充规则归一化与异或孔洞防误判", "PASSED (100%)", "PASSED (100%)"],
        ["TC-12", "当代资产编辑配方与不可变版本继承演进", "PASSED (100%)", "PASSED (100%)"],
        ["TC-13", "权威文献出处索引白名单校验与快照持久化", "PASSED (100%)", "PASSED (100%)"],
        ["TC-14", "十二类程序化三维器型贴附参数生成与无损换器", "PASSED (100%)", "PASSED (100%)"],
        ["TC-15", "工艺透视器双端标尺对角线 169.71mm 数学核算", "PASSED (100%)", "PASSED (100%)"],
        ["TC-16", "DFM 拓扑分析与 4 处承力焊点自动标定", "PASSED (100%)", "PASSED (100%)"],
        ["TC-17", "打样需求入库与后台 ADMIN_PASSWORD Bearer 鉴权", "PASSED (100%)", "PASSED (100%)"],
        ["TC-18", "打样用户个人隐私数据在前台 API 的脱敏隔离", "PASSED (100%)", "PASSED (100%)"],
        ["TC-19", "停机热备份数据复制与文件完整性校验", "PASSED (100%)", "PASSED (100%)"],
        ["TC-20", "恢复至全新独立数据卷并校验当代资产完整读回", "PASSED (100%)", "PASSED (100%)"]
    ]
    builder.add_table(tests_data[0], tests_data[1:], col_widths=[0.9, 3.1, 1.0, 1.0])

    builder.add_heading_2("6.2 安全性与健壮性审计规范")
    builder.add_bullet("输入防注入：上传文件严格限制最大 20 MB，解压包限制 100 MB；全面防御 XML 外部实体（XXE）与 Zip 炸弹攻击。", bold_prefix="文件安全：")
    builder.add_bullet("权限最小化：Docker 容器内部强制以非特权专用用户 (UID 10001:10001) 运行，禁止 root 越权挂载；管理接口强制 Bearer Token 常量时间比对（secrets.compare_digest），杜绝时序侧信道攻击。", bold_prefix="运行时安全：")
    builder.add_bullet("前端依赖合规：本轮构建前执行 npm audit 审计，已知安全漏洞数量严格为 0 条；全量使用本地开源字体与无版权隐患静态资源。", bold_prefix="依赖安全：")

    out_path = ROOT / "docs" / "锡语华纹_系统交付与镜像复现评审手册.docx"
    builder.save(str(out_path))

if __name__ == "__main__":
    build_reproduction_guide()
