# PythonAnywhere 免费部署

## 当前服务

- 网站：`https://xiyuhuawen.pythonanywhere.com`
- PythonAnywhere 用户：`xiyuhuawen`
- 运行时：Python 3.11 + FastAPI + a2wsgi
- 源码目录：`/home/xiyuhuawen/site`
- 虚拟环境：`/home/xiyuhuawen/.virtualenvs/xiyu-venv`
- WSGI 配置：`/var/www/xiyuhuawen_pythonanywhere_com_wsgi.py`
- 持久数据：`/home/xiyuhuawen/site/runtime`（SQLite、收藏、共创资产与打样需求）
- 静态前端：`/home/xiyuhuawen/site/frontend/dist`

## 免费额度与续期

当前服务使用 PythonAnywhere 免费账户，不绑定银行卡。免费账户的磁盘配额为 512 MB，本次部署约占 421 MB。免费网站有到期时间，当前控制台显示为 **2026-12-15**；到期前需要在 Web 控制台点击续期/延长，才能继续保持免费运行。未续期会停止服务，这不是代码故障。

## 运行检查

```bash
curl https://xiyuhuawen.pythonanywhere.com/api/health
```

正常响应为 `{"status":"ok","patterns":60}`。网站重载后收藏数据仍保存在 SQLite 中。

## 更新发布

PythonAnywhere 免费环境没有 Node.js，前端需在本机执行 `npm ci && npm run build`，再将 `frontend/dist` 上传并覆盖到上述目录。后端源码和 `seed` 资源同步后，在 Web 控制台点击 **Reload**。

部署适配器位于 `deploy/pythonanywhere_wsgi.py`。事件循环必须在 uWSGI 工作进程收到首个请求时才创建，不能在主进程导入阶段创建，否则 fork 后公网请求会卡住。

## 管理密码与 API 凭据

后台密码只写入服务器的 WSGI 配置，不进入 GitHub、前端或本地 `.env`。修改后需要 Reload。PythonAnywhere API Token 仅用于部署操作，部署完成后应撤销并在下次需要时重新生成。

## 生成性能

`read_geometry` 使用 `seg.npoint()` 按曲线段批量采样，避免逐点重复计算；无效轮廓才执行拓扑修复。方案比较仍以 24 个候选进行筛选，但仅使用 2 段曲线采样计算指标并返回轻量预览；前端选中方案后立即通过 `/api/creation/preview` 精化，最终编辑、SVG、DXF 和 STL 恢复 12 段精度，交付结果不降级。API 启用 GZip 中间件压缩包含重复 SVG 的 JSON 响应。

## 几何与导出回归

```bash
cd frontend
npm run test:geometry
npm run test:geometry:all
npm run build
```

本次公网验收已覆盖：首页与 3D 预览、60 类纹样目录、设计生成、收藏及 Reload 后持久化、SVG/PNG 导出、DXF 工程包和 STL 导出。DXF 仍由后端原始 SVG 轮廓生成，不经过 Three.js 浮雕网格。
