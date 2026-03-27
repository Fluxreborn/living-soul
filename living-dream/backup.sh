#!/bin/bash
# Living Dream 自动备份脚本

BACKUP_DIR="$HOME/.openclaw/workspace/living-soul-backup"
SOURCE_FILE="$HOME/Projects/livingsoul/living-dream/living-dream-memory.json"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# 如果源文件存在则备份
if [ -f "$SOURCE_FILE" ]; then
    cp "$SOURCE_FILE" "$BACKUP_DIR/living-dream-memory-$TIMESTAMP.json"
    echo "✅ 备份完成: living-dream-memory-$TIMESTAMP.json"
    
    # 清理7天前的备份
    find "$BACKUP_DIR" -name "living-dream-memory-*.json" -mtime +7 -delete
    echo "🧹 已清理7天前的旧备份"
else
    echo "⚠️ 源文件不存在，跳过备份"
fi
