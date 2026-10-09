# ChattiNG 部署指南

## 方式 1: 使用 Render（推荐）

### 步骤：

1. **访问 Render**
   - 打开 https://render.com
   - 用 GitHub 账号登录

2. **连接仓库**
   - 点击 "New +"
   - 选择 "Web Service"
   - 连接你的 GitHub 账户
   - 选择 `Junaylin-0103/ChattiNG` 仓库

3. **配置设置**
   - Name: `chatting` (或任何你喜欢的名字)
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app`
   - Instance Type: `Free`

4. **设置环境变量**
   - 在 Render 仪表盘中，找到 "Environment"
   - 添加这些变量：
     ```
     SECRET_KEY=your_random_secret_key_here
     ADMIN_USERNAME=Junaylin
     ADMIN_PASSWORD=your_strong_password_here
     ```

5. **部署**
   - 点击 "Create Web Service"
   - 等待部署完成（约 2-3 分钟）
   - 你会得到一个 URL，例如 `https://chatting-xxxx.onrender.com`

---

## 方式 2: 使用 Railway

### 步骤：

1. **访问 Railway**
   - 打开 https://railway.app
   - 用 GitHub 账号登录

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择 `Junaylin-0103/ChattiNG`

3. **配置**
   - Railway 会自动检测 `Procfile`
   - 添加环境变量：
     ```
     SECRET_KEY=your_random_secret_key_here
     ADMIN_USERNAME=Junaylin
     ADMIN_PASSWORD=your_strong_password_here
     ```

4. **等待部署**
   - 点击 "Deploy"
   - 完成后你会得到一个公网 URL

---

## 方式 3: 使用 Heroku（需要信用卡，但更稳定）

### 步骤：

1. **安装 Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku

   # Windows (PowerShell)
   choco install heroku-cli
   ```

2. **登录 Heroku**
   ```bash
   heroku login
   ```

3. **创建应用**
   ```bash
   heroku create chatting-app-your-name
   ```

4. **设置环境变量**
   ```bash
   heroku config:set SECRET_KEY=your_random_secret_key_here
   heroku config:set ADMIN_USERNAME=Junaylin
   heroku config:set ADMIN_PASSWORD=your_strong_password_here
   ```

5. **推送部署**
   ```bash
   git push heroku main
   ```

6. **查看应用**
   ```bash
   heroku open
   ```

---

## 生成强 SECRET_KEY

在 Python 中运行：

```python
import secrets
print(secrets.token_hex(32))
```

或在命令行：

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 常见问题

### Q: 为什么消息在刷新后消失？
**A:** 目前数据库是本地文件。部署到云服务器后，每次重启应用都会重置数据库。

**解决方案：** 升级到付费数据库（PostgreSQL）或使用 Redis。

### Q: 免费服务会不会休眠？
**A:** 
- Render 的免费层在 15 分钟无请求后会休眠
- Railway 有免费积分，用完后暂停
- Heroku 的免费层已停用

**建议：** 使用 Railway 或 Render，它们对小项目足够了。

### Q: 可以用自己的域名吗？
**A:** 可以。每个平台都支持自定义域名，需要配置 DNS 记录。

---

## 下一步

部署成功后，你会得到一个 URL，例如：

```
https://chatting-xxxx.onrender.com
```

分享这个 URL 给朋友，他们就能直接访问你的聊天室！

---

## 需要帮助？

如果部署有问题，请检查：
1. 所有环境变量是否设置正确
2. `requirements.txt` 是否包含所有依赖
3. `Procfile` 中的启动命令是否正确
