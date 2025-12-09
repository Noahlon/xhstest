# 确保 platform-tools 目录存在（没有就建一个）
mkdir -p "$HOME/Library/Android/sdk/platform-tools"

# 创建符号链接
ln -s /opt/homebrew/bin/adb "$HOME/Library/Android/sdk/platform-tools/adb"

# 验证
ls -l "$HOME/Library/Android/sdk/platform-tools/adb"
# 应该输出：adb -> /opt/homebrew/bin/adb
