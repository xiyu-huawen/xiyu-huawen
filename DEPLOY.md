# Fly.io 部署

## 当前资源

- 应用：`xiyu-huawen`
- 地址：`https://xiyu-huawen.fly.dev`
- 区域：新加坡 `sin`
- 持久卷：`xiyu_data`，挂载到 `/data`
- 容器：Nginx + FastAPI，内部端口 `8080`
- 实例：固定 1 台，SQLite 与单卷挂载不启用多副本
- 挂载：通过 `fly.toml` 的 `[mounts]` 配置，卷附加到生产机器

## 更新发布

```bash
../.runtime/fly/flyctl deploy --remote-only --app xiyu-huawen
```

前端在远程构建阶段执行 `npm ci && npm run build`。后端使用 `backend/requirements.lock` 安装依赖。

## 管理密码

管理密码只保存在 Fly Secrets，不进入源码或镜像。需要重置时执行：

```bash
../.runtime/fly/flyctl secrets set ADMIN_PASSWORD='替换为新的强随机密码' --app xiyu-huawen
```

## 运行检查

```bash
curl https://xiyu-huawen.fly.dev/api/health
../.runtime/fly/flyctl status --app xiyu-huawen
../.runtime/fly/flyctl logs --app xiyu-huawen
```

持久卷包含设计、收藏、共创资产与打样需求。删除应用或卷会同时删除这些数据，操作前必须另行备份。

## 浮雕几何回归

```bash
cd frontend
npm run test:geometry
npm run test:geometry:all
npm run build
```

全量检查覆盖所有可复用矢量资产的实体生成、嵌套轮廓、粗描边展开、重复点清理和坐标有效性。DXF 由后端原始 SVG 轮廓生成，不经过 Three.js 浮雕网格。
