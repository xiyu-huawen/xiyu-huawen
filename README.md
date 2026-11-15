# 锡语华纹

面向新生杯参赛及实际设计协作的传统纹样造物平台。支持通用Linux Docker Compose部署，默认不需要AI服务。

## 使用交付镜像启动

1. 按服务器架构选择`outputs/1.3.0/xiyuhuawen-1.3.0-arm64.tar.gz`或`outputs/1.3.0/xiyuhuawen-1.3.0-amd64.tar.gz`。
2. 用`shasum -a 256 -c outputs/1.3.0/SHA256SUMS`校验镜像包。
3. `docker load -i outputs/1.3.0/xiyuhuawen-1.3.0-arm64.tar.gz`（AMD64换对应文件）。
4. `cp .env.example .env`，设置强随机`ADMIN_PASSWORD`和相应`IMAGE_TAG=1.3.0-arm64`或`1.3.0-amd64`。
5. `docker compose up -d --no-build`，访问`http://服务器地址:8088`。

本机预览已使用随机生成的`.env`，后台密码从该文件读取；不要把`.env`提交或上传公共仓库。公网使用时在上层反向代理启用HTTPS，后台密码随服务器妥善保管。

## 构建与开发

- `docker compose build`：依赖已锁定，按精确基础镜像tag构建。
- `scripts/package.sh`：构建双架构镜像并打包校验值，需要可访问软件包与镜像源。
- 后端：Python 3.11，`pip install -r backend/requirements.lock`，安装系统`libcairo2`，运行`uvicorn backend.app:app --reload`。
- 前端：`cd frontend && npm ci && npm run dev`，Vite将API请求转发到8000端口。
- 文档全量导入：`python -m backend.ingest 原始内容/数据 seed`。解析仅通过PAT开头的真实DOCX，忽略Office临时文件。
- 测试：`python -m pytest tests -q`；前端：`npm run build`。

## AI辅助（可选）

`.env`中设置`AI_BASE_URL`（例如兼容服务的/v1地址）、`AI_MODEL`和`AI_API_KEY`。不配置时使用规则生成。模型只提取意图关键词与白名单基因，不生成任意图形或未经证实的解释。

## 升级、回滚与备份

持久卷由Compose管理，默认项目目录名为xsb时为`xsb_xiyu-data`。不要用`docker compose down -v`，该命令会删除业务数据。

备份：先`docker compose stop api`，再用`docker compose cp api:/data ./backup-data`，最后`docker compose start api`。必须复制整个目录，包括SQLite、catalog、uploads与assets；首次使用备份目标须不存在或为空。

恢复：停止API，`docker compose cp ./backup-data/. api:/data/`，检查文件归属为10001:10001，再启动API。恢复前保留现有数据副本；只恢复相同版本或已验证兼容版本的备份。

升级：先备份，加载新镜像，在`.env`中切换IMAGE_TAG，`docker compose up -d --no-build`。回滚切回旧镜像tag；若新版本更改数据结构，应同时恢复升级前数据。本版本没有自动破坏性迁移。

健康检查：`curl http://localhost:8088/api/health`；日志：`docker compose logs --tail=100`。日志按10MB×3轮转。

## 接口

`GET /api/catalog`、`GET /api/patterns?q=&word=&category=`、`GET /api/patterns/{id}`、`GET /api/genes?q=`、`GET /api/imagery`；`POST /api/intent`、`POST /api/designs`、`GET /api/designs/{id}`、`PUT /api/designs/{id}/favorite`、`GET /api/designs`（共享收藏）、`GET /api/designs/{id}/export/{svg|png}`。

管理：`GET /api/admin/report`、`POST /api/admin/import`（multipart file），使用`Authorization: Bearer <ADMIN_PASSWORD>`。交互文档：后端`/docs`（容器内8000端口，默认未向宿主机暴露）。

更多建设边界见[建设方案与交付说明](docs/建设方案与交付说明.md)，实际架构测试结果见[验收记录](docs/验收记录.md)。

## 当前预览与第二版体验

本机已部署新版到`http://localhost:8098`。默认8088端口在本机已被其他应用占用，因此仅当前`.env`改为8098；新服务器可自行设置PORT。

新版包含纹样书房、可交互图谱、构图实验、逐步纹样阅读、三层真实图元选配和三维材质／拆解探索。知识内容均标明项目资料出处，不将候选关系写成确定结论。

设计导出增加`GET /api/designs/{id}/export/json`。`POST /api/designs`支持`layers:[{pattern_id,code,role}]`（role为center/ring/accent）、`rotation`及`width_mm/height_mm`。SVG尺寸是设计平面尺寸，不等同工厂刀模。


## 参赛交付版 1.1.0

首屏直接进入造物，支持定意、探源、方向比较、共创、成器。提供24参数候选评估、六种构图、锚点锁定、几何融合/反刻/轮廓、手绘排列轨迹、版本历史与七种器物预览。

工程包：作品成器后下载ZIP，内含1:1毫米制DXF、SVG、参数JSON、设计与来源档案、交付说明。DXF已验证闭合轮廓、孔洞、单位及读回坐标；设备参数未确认，定位为工坊制版沟通文件，不包含机床指令或加工认证。

打样需求：成器页填写数量、说明与选填联系方式，可提交到项目团队队列。在“资料管理”输入ADMIN_PASSWORD后处理状态。此操作不自动通知工厂、不确认订单或报价。

AI意境图：设置IMAGE_API_KEY、IMAGE_BASE_URL、IMAGE_MODEL后启用参考图编辑。未配置时明确提示；默认每天最多10个任务，可用IMAGE_DAILY_LIMIT调整。相同参考图和版本复用结果，不自动重试付费任务。当前未配置有效服务密钥，因此真实出图尚未验收。

当前为共享项目空间与作品集，不提供个人账户、支付或自动生产系统。创作草稿保存在浏览器与持久卷中；版本历史保留最近20步。管理员接口受后台密码保护，打样联系方式不在公开状态查询中返回。

本轮最新交付物统一放在outputs/1.3.0，原1.0.0交付物保留用于回滚。参赛演示说明见docs/参赛交付版1.1.md。

## 1.2.0 纹样星球与十二器物

整站使用同一导航与墨色、锡银、暖金主题。纹样星球支持缓慢自转、暂停、节点拖动、关系高亮、随选知识阅读和直接入器。十二类本地程序化三维器型支持保留当前纹样换器；工艺透视器使用配方毫米尺寸，提供两点测距、角度和坐标微调。

最新发布文件位于outputs/1.3.0；此前版本保留用于回滚。产品特色与展示路线见docs/产品特色与参赛展示路线.md。AI服务未配置时不影响结构创作、保存与工程文件导出；屏幕预览和手动测距不替代工坊打样。

## 1.3.0 活态共创与知识资产

器物视图、操作栏、来源与编辑器使用独立布局。器物默认缓慢环视，拖动时暂停，松开1.5秒后恢复；主动暂停与减少动态设置受到尊重。

共创工坊提供自由画笔、花瓣/圆/方形、对称及镜像、选取拖动、缩放旋转、图层整理和SVG/透明PNG导出。作品保存为独立的当代创作资产，保留可编辑笔画、底稿与版本来源，可继续入器及再编辑。它们不自动获得传统寓意认证。此版本为项目共享空间，不提供独立用户账户与私人作品权限。

书房共17篇文章，其中10篇补充公开机构资料，来源索引包含13条机构链接。文章内容随站点本地交付；点击外部出处需要联网。参考文章编号由服务端白名单核验，其来源快照随设计、派生资产和工程档案保存。

社区接口：GET/POST /api/community/patterns、GET /api/community/patterns/{id}。SQLite和/data/assets保存新作、编辑记录、彩色原图与安全金属轮廓；备份须包含整个数据卷。资产入库会进行SVG安全、可见轮廓、填充规则和容量校验。版权/底稿使用权由提交者确认，不等于平台完成权属认证。
