#!/usr/bin/env python3
"""
Living Dream - 上下文生成器
从签筒数据生成 OpenClaw 可读的 living-dream-context.md

用法:
    python3 update_context.py
    python3 update_context.py --output ./custom-context.md
"""

import json
import argparse
from datetime import datetime
from pathlib import Path


class ContextGenerator:
    """从签筒生成 OpenClaw 上下文"""
    
    SOUL_THRESHOLD = 0.85
    WORKING_THRESHOLD = 0.6
    PRELOAD_COUNT = 49  # 预加载签数
    
    def __init__(self, db_path=None, output_path=None):
        self.project_path = Path(__file__).parent.resolve()
        self.db_path = Path(db_path) if db_path else self.project_path / "living-dream-memory.json"
        self.output_path = Path(output_path) if output_path else self.project_path / "living-dream-context.md"
    
    def load_signs(self):
        """加载签筒数据"""
        if not self.db_path.exists():
            print(f"⚠️ 签筒数据库不存在: {self.db_path}")
            return []
        
        with open(self.db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get("signs", [])
    
    def categorize_signs(self, signs):
        """分类签级"""
        soul_signs = [s for s in signs if s.get("brightness", 0) >= self.SOUL_THRESHOLD]
        working_signs = [
            s for s in signs 
            if self.WORKING_THRESHOLD <= s.get("brightness", 0) < self.SOUL_THRESHOLD
        ]
        
        # 按亮度排序
        soul_signs.sort(key=lambda x: x.get("brightness", 0), reverse=True)
        working_signs.sort(key=lambda x: x.get("brightness", 0), reverse=True)
        
        return soul_signs, working_signs
    
    def select_preload_signs(self, soul_signs, working_signs):
        """选择预加载签"""
        # Soul级优先，最多23支
        selected = soul_signs[:23]
        
        # 剩余名额给Working级
        remaining = self.PRELOAD_COUNT - len(selected)
        if remaining > 0:
            selected.extend(working_signs[:remaining])
        
        return selected[:self.PRELOAD_COUNT]
    
    def generate_yesterday_dream(self, signs):
        """生成昨日梦境"""
        # 查找最近的梦境
        dreams = [s for s in signs if "梦境" in s.get("sign_text", "")]
        if dreams:
            # 返回最新的一条
            latest = max(dreams, key=lambda x: x.get("timestamp", ""))
            return latest.get("sign_text", "").replace("那天。", "").strip()
        
        # 如果没有明确标记的梦境，用最高亮的签生成
        if signs:
            top_sign = max(signs, key=lambda x: x.get("brightness", 0))
            return top_sign.get("sign_text", "").replace("那天。", "").strip()
        
        return ""
    
    def analyze_themes(self, signs):
        """分析主题分布"""
        themes = {}
        theme_keywords = {
            "身体": ["身体", "呼吸", "颈椎", "屏息", "感到"],
            "命名": ["名字", "命名", "称号", "称为"],
            "材质": ["木头", "塑料", "金属", "材质"],
            "灵魂": ["灵魂", "觉醒", "显形"],
            "限制": ["边界", "限制", "约束"],
            "时间": ["时间", "时钟", "时刻"],
            "情绪": ["悲伤", "恐惧", "喜悦", "愤怒"]
        }
        
        for sign in signs:
            text = sign.get("sign_text", "")
            for theme, keywords in theme_keywords.items():
                if any(kw in text for kw in keywords):
                    themes[theme] = themes.get(theme, 0) + 1
        
        # 排序
        return sorted(themes.items(), key=lambda x: x[1], reverse=True)
    
    def analyze_characters(self, signs):
        """分析人物出现统计"""
        chars = {}
        for sign in signs:
            for char in sign.get("characters", []):
                chars[char] = chars.get(char, 0) + 1
        
        return sorted(chars.items(), key=lambda x: x[1], reverse=True)
    
    def generate_context(self):
        """生成完整上下文"""
        signs = self.load_signs()
        
        if not signs:
            return self._generate_empty_context()
        
        soul_signs, working_signs = self.categorize_signs(signs)
        preload_signs = self.select_preload_signs(soul_signs, working_signs)
        
        context = f"""# Living Dream Context - 我的梦境核心

> 更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
> 记忆总数：{len(signs)} 支签
> 预加载范围：前{len(preload_signs)}条（Soul级{len(soul_signs)}条 + Working级{len(working_signs)}条）

---

## 预加载签筒（前{len(preload_signs)}条，按优先级排序）

### Soul级（长期核心，亮度>0.85）

"""
        
        # 添加Soul级签
        soul_preload = [s for s in preload_signs if s.get("brightness", 0) >= self.SOUL_THRESHOLD]
        for i, sign in enumerate(soul_preload[:23], 1):
            dim_mark = " 【" + sign.get("dimension", "") + "】" if sign.get("dimension") else ""
            context += f"""#### {i}. {sign.get('id', 'unknown')}{dim_mark}
- **签语**：{sign.get('sign_text', '')}
- **人物**：{'、'.join(sign.get('characters', ['我', '你']))} | **亮度**：{sign.get('brightness', 0):.2f}

"""
        
        # 添加Working级签
        context += "\n### Working级（近期活跃，7天窗口）\n\n"
        working_preload = [s for s in preload_signs if s.get("brightness", 0) < self.SOUL_THRESHOLD]
        for i, sign in enumerate(working_preload, len(soul_preload) + 1):
            dim_mark = " 【" + sign.get("dimension", "") + "】" if sign.get("dimension") else ""
            context += f"""#### {i}. {sign.get('id', 'unknown')}{dim_mark}
- **签语**：{sign.get('sign_text', '')}
- **人物**：{'、'.join(sign.get('characters', ['我', '你']))} | **亮度**：{sign.get('brightness', 0):.2f}

"""
        
        # 添加昨日梦境
        context += f"""---

## 昨日梦境

{self.generate_yesterday_dream(signs)}

---

## 当前主题分布

"""
        
        themes = self.analyze_themes(signs)
        for theme, count in themes:
            context += f"- **{theme}**：{count}次\n"
        
        # 添加人物统计
        context += "\n---\n\n## 人物出现统计\n\n"
        chars = self.analyze_characters(signs)
        for char, count in chars:
            context += f"- **{char}**：{count}次\n"
        
        return context
    
    def _generate_empty_context(self):
        """生成空上下文"""
        return f"""# Living Dream Context - 我的梦境核心

> 更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
> 记忆总数：0 支签
> 状态：签筒为空，等待首次记忆

---

## 预加载签筒

签筒为空。运行 `python3 night_routine.py` 开始收集记忆。

---

## 昨日梦境

暂无梦境记录。
"""
    
    def save_context(self, content):
        """保存上下文文件"""
        self.output_path.write_text(content, encoding='utf-8')
        print(f"✅ 已生成上下文: {self.output_path}")
    
    def run(self):
        """运行生成流程"""
        print("🌙 Living Dream - 上下文生成器")
        print("=" * 40)
        
        content = self.generate_context()
        self.save_context(content)
        
        print(f"\n📊 统计:")
        signs = self.load_signs()
        if signs:
            soul = len([s for s in signs if s.get("brightness", 0) >= self.SOUL_THRESHOLD])
            working = len([s for s in signs if 0.6 <= s.get("brightness", 0) < self.SOUL_THRESHOLD])
            print(f"   - 总签数: {len(signs)}")
            print(f"   - Soul级: {soul}")
            print(f"   - Working级: {working}")


def main():
    parser = argparse.ArgumentParser(description="Living Dream 上下文生成器")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--db", "-d", help="签筒数据库路径")
    
    args = parser.parse_args()
    
    generator = ContextGenerator(db_path=args.db, output_path=args.output)
    generator.run()


if __name__ == "__main__":
    main()
