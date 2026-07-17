# 国服资源包说明

此目录用于存放**国服（胜利女神：新的希望）**专用的资源文件。

## 初始化步骤（必须执行）

目前此目录为空，请按以下步骤完成初始化：

### 方法一：本地复制（推荐）

在项目根目录执行（PowerShell）：

```powershell
Copy-Item -Path "assets\resource" -Destination "assets\resource_cn" -Recurse -Force
```

或使用 Git Bash / CMD：

```bash
cp -r assets/resource/* assets/resource_cn/
```

### 方法二：手动复制

将 `assets/resource` 文件夹下的所有内容完整复制到 `assets/resource_cn` 中。

---

## 后续适配工作

复制完成后，国服资源包会先使用国际服的模板图片作为基础。

由于国服与国际服存在 UI 差异，部分功能可能识别失败。你需要：

1. 开启调试模式，运行出问题的任务
2. 对比国服实际截图与模板图片的差异
3. 替换 `assets/resource_cn/image/` 下对应的 PNG 模板
4. 必要时调整 pipeline 中的 ROI 区域

常见需要优先检查/替换的位置：
- 登录与服务器选择界面
- 主界面按钮
- 商店相关界面
- 活动入口与奖励领取
- 部分弹窗确认按钮

---

**注意**：此国服适配仅为个人使用修改，请勿公开发布。
