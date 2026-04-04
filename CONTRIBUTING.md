# Contributing to FishRouter

欢迎为 FishRouter 贡献代码、文档或建议！请阅读以下指南。

---

## 开发环境

```bash
git clone https://github.com/Aobing-code/fishrouter.git
cd fishrouter
python3 -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
cp config.example.json config.json
```

运行：

```bash
python -m app.main
```

访问 `http://localhost:8080` 查看面板。

---

## 代码规范

- 遵循 PEP 8（Python）
- 新增功能需写测试（`tests/` 目录）
- 提交信息请使用 [Conventional Commits](https://www.conventionalcommits.org/)：
  - `feat:` 新功能
  - `fix:` 缺陷修复
  - `docs:` 文档变更
  - `refactor:` 重构
  - `test:` 测试相关
  - `chore:` 构建/工具变更

示例：

```
feat: add /healthz backend check
fix: handle missing backend status gracefully
docs: update quickstart with Docker notes
```

---

## 提交流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feat/my-feature`)
3. 进行修改并提交 (`git commit -m "feat: ..."`)
4. 推送到你的远程 (`git push origin feat/my-feature`)
5. 开启 Pull Request，描述变更内容和动机

---

## 测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行测试
pytest tests/
```

请确保新增代码有相应的测试覆盖。

---

## 配置文件验证

新增的 `scripts/configtest.py` 可用于检查 `config.json` 语法和后端连通性：

```bash
python scripts/configtest.py
```

---

## 行为准则

- 尊重所有社区成员
- 接受建设性反馈
- 关注提问与帮助

---

感谢你的贡献！🐟
