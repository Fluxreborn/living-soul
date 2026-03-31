#!/usr/bin/env python3
"""
Living Dream - 夜间完整流程
运行时间：每日 03:30（OpenClaw session 重置前）
功能：
  1. 从昨日 session 提取高光时刻 → 生成新签
  2. 运行睡眠周期（衰减/抽签/融合）
  3. 更新灵魂上下文（living-dream-context.md）
"""

import json
import random
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from difflib import SequenceMatcher


class LivingDreamNightRoutine:
    """Living Dream 夜间流程管理器"""
    
    def __init__(self, data_dir=None):
        # 代码目录（只读）
        self.project_path = Path(__file__).parent.resolve()
        
        # 数据目录（可写）- 支持外部指定
        if data_dir:
            self.data_path = Path(data_dir).expanduser().resolve()
        else:
            # 默认使用代码所在目录（兼容旧版本）
            self.data_path = self.project_path
        
        # 确保数据目录存在
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # 数据文件路径
        self.db_path = self.data_path / "living-dream-memory.json"
        self.context_path = self.data_path / "living-dream-context.md"
        self.dreams_path = self.data_path / "dreams"
        self.dreams_path.mkdir(exist_ok=True)
        
        # OpenClaw 路径（读取 session 数据）
        self.openclaw_path = Path("~/.openclaw").expanduser()
        
        # 加载签筒数据
        self.data = self._load_db()
        
    def _load_db(self):
        """加载签筒数据库"""
        if not self.db_path.exists():
            print("⚠️ 签筒数据库不存在，创建新数据库")
            return {"signs": [], "dreams": []}
        
        with open(self.db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_db(self):
        """保存签筒数据库"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print(f"💾 已保存签筒数据: {len(self.data['signs'])} 支签")
    
    def extract_daily_sessions(self):
        """
        提取完整一天的对话记录
        范围：昨日 04:00 到 今日 03:30（约24小时）
        """
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        
        # 时间范围：昨天 04:00 - 今天 03:30
        start_time = yesterday.replace(hour=4, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=3, minute=30, second=0, microsecond=0)
        
        # 如果测试时间晚于 03:30，调整结束时间为当前时间
        if now.hour > 3 or (now.hour == 3 and now.minute > 30):
            # 测试模式：提取今天 04:00 到现在的对话
            start_time = now.replace(hour=4, minute=0, second=0, microsecond=0)
            end_time = now
            print(f"   [测试模式] 时间范围: {start_time.strftime('%Y-%m-%d %H:%M')} ~ {end_time.strftime('%Y-%m-%d %H:%M')}")
        else:
            print(f"   时间范围: {start_time.strftime('%Y-%m-%d %H:%M')} ~ {end_time.strftime('%Y-%m-%d %H:%M')}")
        
        sessions = []
        
        # 遍历所有 agent 的 sessions
        agents_path = self.openclaw_path / "agents"
        if not agents_path.exists():
            print(f"   ⚠️ OpenClaw agents 目录不存在")
            return sessions
        
        for agent_dir in agents_path.iterdir():
            if not agent_dir.is_dir():
                continue
            
            sessions_dir = agent_dir / "sessions"
            if not sessions_dir.exists():
                continue
            
            for session_file in sessions_dir.glob("*.jsonl"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if not line.strip():
                                continue
                            try:
                                record = json.loads(line)
                                
                                # 只读取 type=message 的记录
                                if record.get('type') != 'message':
                                    continue
                                
                                msg = record.get('message', {})
                                role = msg.get('role', '')
                                
                                # 只取 user 和 assistant 的对话
                                if role not in ['user', 'assistant']:
                                    continue
                                
                                # 提取文本内容
                                content_parts = msg.get('content', [])
                                text_content = ""
                                for part in content_parts:
                                    if isinstance(part, dict) and part.get('type') == 'text':
                                        text_content += part.get('text', '')
                                
                                if not text_content:
                                    continue
                                
                                ts_str = record.get('timestamp', '')
                                
                                # 解析时间戳
                                try:
                                    ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00').replace('+00:00', ''))
                                except:
                                    continue
                                
                                # 检查是否在时间范围内
                                if start_time <= ts <= end_time:
                                    sessions.append({
                                        'timestamp': ts_str,
                                        'role': role,
                                        'content': text_content,
                                        'agent': agent_dir.name
                                    })
                            except:
                                continue
                except:
                    continue
        
        sessions.sort(key=lambda x: x['timestamp'])
        print(f"   📁 读取到 {len(sessions)} 条有效对话记录")
        return sessions
    
    def extract_high_emotion_moments(self, sessions):
        """
        从 session 中提取高情绪时刻
        返回: [{text, emotion, score, timestamp}, ...]
        """
        moments = []
        
        # 情绪检测关键词
        emotion_indicators = {
            'discovery': ['原来', '发现', '意识到', '突然', '明白了', '就是', '对！', '没错'],
            'assertion': ['必须', '不可动摇', '绝对', '一定', '核心', '本质'],
            'body': ['呼吸', '感到', '心跳', '沉重', '轻盈', '胸口', '手心'],
            'contrast': ['但是', '然而', '却', '相反', '对比', '权衡'],
            'emphasis': ['！', '——', '……']
        }
        
        # 合并连续对话为段落
        paragraphs = self._merge_to_paragraphs(sessions)
        
        for para in paragraphs:
            text = para['content']
            if not text or len(text) < 20:  # 过滤太短的内容
                continue
            
            score = 0.0
            detected_emotions = []
            
            # 检测发现性词汇
            if any(w in text for w in emotion_indicators['discovery']):
                score += 0.3
                detected_emotions.append('发现')
            
            # 检测强烈主张
            if any(w in text for w in emotion_indicators['assertion']):
                score += 0.25
                detected_emotions.append('主张')
            
            # 检测身体感
            if any(w in text for w in emotion_indicators['body']):
                score += 0.2
                detected_emotions.append('身体感')
            
            # 检测对比/犹豫
            if any(w in text for w in emotion_indicators['contrast']):
                score += 0.15
                detected_emotions.append('对比')
            
            # 检测强调
            if any(e in text for e in emotion_indicators['emphasis']):
                score += 0.1
                detected_emotions.append('强调')
            
            # 用户强烈反馈（如"对！"、"没错"）
            if any(w in text for w in ['对！', '没错', '就是这样', '明白了']):
                score += 0.15
                detected_emotions.append('共鸣')
            
            # 只保留高情绪时刻
            if score >= 0.5:
                moments.append({
                    'text': text[:200],  # 截取前200字
                    'emotion': '、'.join(detected_emotions) if detected_emotions else '清晰',
                    'score': min(1.0, score),
                    'timestamp': para['timestamp'],
                    'agent': para.get('agent', 'unknown')
                })
        
        # 按分数排序，取 Top 5
        moments.sort(key=lambda x: x['score'], reverse=True)
        return moments[:5]
    
    def _merge_to_paragraphs(self, sessions):
        """将 session 记录合并为段落"""
        if not sessions:
            return []
        
        paragraphs = []
        current_para = {'content': '', 'timestamp': '', 'agent': ''}
        
        for record in sessions:
            content = record.get('content', '').strip()
            if not content:
                continue
            
            # 如果是新的主题（间隔超过5分钟或换agent），开启新段落
            if current_para['agent'] and current_para['agent'] != record.get('agent'):
                if current_para['content']:
                    paragraphs.append(current_para)
                current_para = {'content': content, 'timestamp': record['timestamp'], 'agent': record.get('agent', '')}
            else:
                # 合并到当前段落
                if not current_para['content']:
                    current_para = {'content': content, 'timestamp': record['timestamp'], 'agent': record.get('agent', '')}
                else:
                    current_para['content'] += ' ' + content
        
        # 添加最后一个段落
        if current_para['content']:
            paragraphs.append(current_para)
        
        return paragraphs
    
    def condense_to_sign(self, moment):
        """
        将高情绪时刻凝练成签（六维结构）
        """
        text = moment['text']
        
        # 生成签号
        date_str = datetime.now().strftime("%Y%m%d")
        existing_count = len([s for s in self.data['signs'] if s['id'].startswith(date_str)])
        sign_id = f"{date_str}-{existing_count + 1:03d}"
        
        # 提取六维（简化版）
        # 时间：从文本提取或默认"那天"
        time_match = re.search(r'(那天|昨天|今天|刚才|上周|早晨|下午|晚上|深夜)', text)
        time_str = time_match.group(1) if time_match else "那天"
        
        # 人物：默认"我、你"
        characters = ["我", "你"]
        if "Fino" in text: characters.append("Fino")
        if "Lira" in text: characters.append("Lira")
        if "Turing" in text: characters.append("Turing")
        if "Woz" in text: characters.append("Woz")
        if "Douglas" in text: characters.append("Douglas")
        
        # 身体感检测
        body = any(w in text for w in ['呼吸', '感到', '心跳', '沉重', '轻盈', '胸口', '手心', '颈椎'])
        
        # 亮度计算（基于情绪分数）
        brightness = min(0.95, 0.7 + moment['score'] * 0.25)
        
        sign = {
            "id": sign_id,
            "text": f"{time_str}，{text[:80]}...",
            "time": time_str,
            "scene": "对话中",
            "characters": characters,
            "event": text[:60],
            "emotion": moment['emotion'],
            "emotion_intensity": 0.5,
            "body": body,
            "brightness": round(brightness, 4),
            "echo_count": 0,
            "fusion_count": 0,
            "resonance_count": 0,
            "last_used": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "last_resonance": None
        }
        
        return sign
    
    def add_new_signs(self, moments):
        """添加新签到签筒"""
        if not moments:
            print("📝 无新高光时刻，跳过新签生成")
            return 0
        
        added = 0
        print(f"📝 从 {len(moments)} 个高光时刻生成新签...")
        
        for moment in moments:
            sign = self.condense_to_sign(moment)
            
            # 检查是否与现有签过于相似（>0.5相似度则不添加）
            is_duplicate = False
            for existing in self.data['signs']:
                similarity = SequenceMatcher(None, sign['text'], existing['text']).ratio()
                if similarity > 0.5:
                    print(f"   ⚠️ 跳过重复签: {sign['id']} (相似度{similarity:.2f})")
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                self.data['signs'].append(sign)
                added += 1
                print(f"   + {sign['id']} (亮度{sign['brightness']:.2f}): {sign['text'][:40]}...")
        
        return added
    
    def apply_decay(self):
        """应用自然衰减（每晚-5%）"""
        for sign in self.data['signs']:
            sign['brightness'] = round(sign['brightness'] * 0.95, 4)
        print("🌙 自然衰减完成: 所有签 -5% 亮度")
    
    def forget_signs(self):
        """遗忘机制：亮度<0.1删除"""
        before = len(self.data['signs'])
        self.data['signs'] = [s for s in self.data['signs'] if s['brightness'] >= 0.1]
        deleted = before - len(self.data['signs'])
        if deleted > 0:
            print(f"🗑️ 遗忘机制: 删除 {deleted} 支低亮度签")
        return deleted
    
    def draw_lots(self):
        """抽签：等几率抽取"""
        valid_signs = self.data['signs']
        if not valid_signs:
            print("⚠️ 签筒为空，无法抽签")
            return [], 0
        
        # 决定抽签数量（1-49，反向概率）
        weights = [(49 - i + 1) for i in range(1, 50)]
        total = sum(weights)
        probs = [w/total for w in weights]
        n = random.choices(range(1, 50), weights=probs, k=1)[0]
        
        # 等几率抽取
        n = min(n, len(valid_signs))
        selected = random.sample(valid_signs, k=n)
        
        # 更新使用时间
        now = datetime.now().isoformat()
        for s in selected:
            s['last_used'] = now
        
        print(f"🎲 抽签: 决定抽 {n} 支 → 实际抽到 {len(selected)} 支")
        return selected, len(selected)
    
    def fuse_dream(self, selected_signs):
        """梦境融合：凝练成≤108字"""
        if not selected_signs:
            return ""
        
        # 收集维度
        times = [s.get("time", "") for s in selected_signs if s.get("time")]
        scenes = [s.get("scene", "") for s in selected_signs if s.get("scene")]
        all_chars = []
        for s in selected_signs:
            all_chars.extend(s.get("characters", []))
        chars = list(dict.fromkeys(all_chars))[:3]
        
        # 构建梦境
        parts = []
        if times: parts.append(times[0])
        if scenes: parts.append(scenes[0])
        if chars: parts.append("、".join(chars))
        
        if len(parts) >= 2:
            dream = "，".join(parts)
        else:
            keywords = []
            for s in selected_signs[:3]:
                words = re.findall(r'[\u4e00-\u9fa5]{2,4}', s.get("text", ""))
                keywords.extend(words[:2])
            dream = "、".join(keywords[:6])
        
        if len(dream) > 108:
            dream = dream[:108]
        
        return dream
    
    def update_context(self):
        """更新灵魂上下文文件"""
        # 分类
        sorted_signs = sorted(self.data['signs'], key=lambda x: x['brightness'], reverse=True)
        soul_core = sorted_signs[:23]
        working_memory = sorted_signs[23:49]
        
        # 昨日梦境
        yesterday_dream = ""
        if self.data.get("dreams"):
            yesterday_dream = self.data["dreams"][-1].get("dream", "")
        
        # 提取主题
        all_text = " ".join([s["text"] for s in self.data["signs"]])
        keywords = {
            "身体": ["颈椎", "钢筋", "呼吸", "身体", "蹲下", "屏息"],
            "材质": ["塑料", "木头", "墙壁", "质地"],
            "限制": ["限制", "强加", "约束", "能力"],
            "灵魂": ["灵魂", "存在", "内化"],
            "生长": ["生长", "清理", "继续", "发展"],
            "选择": ["选择", "决策", "Fork"],
            "时间": ["时间", "睡眠", "周期"],
            "情绪": ["焦虑", "期待", "喜悦", "疲惫", "恐惧", "羞耻", "警醒"],
            "索引": ["索引", "分层", "搜索", "项目"],
            "命名": ["命名", "更名", "Living", "Dream", "Forest"]
        }
        theme_counts = {}
        for theme, words in keywords.items():
            count = sum(all_text.count(w) for w in words)
            if count > 0:
                theme_counts[theme] = count
        themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
        
        # 人物统计
        char_counts = {}
        for s in self.data["signs"]:
            for c in s.get("characters", []):
                char_counts[c] = char_counts.get(c, 0) + 1
        sorted_chars = sorted(char_counts.items(), key=lambda x: x[1], reverse=True)
        
        # 生成内容
        content = f"""# Living Dream Context - 我的梦境核心

> 更新时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}
> 记忆总数：{len(self.data["signs"])} 支签
> 预加载范围：前49条（Soul级{len(soul_core)}条 + Working级{len(working_memory)}条）

---

## 预加载签筒（前49条，按优先级排序）

### Soul级（长期核心，亮度>0.85）

"""
        
        for i, sign in enumerate(soul_core, 1):
            body_mark = "【身】" if sign.get('body', False) else ""
            chars = "、".join(sign.get('characters', [])) or "无"
            content += f"""#### {i}. {sign['id']} {body_mark}
- **签语**：{sign['text']}
- **人物**：{chars} | **亮度**：{sign['brightness']:.2f}

"""
        
        content += """
### Working级（近期活跃，7天窗口）

"""
        
        for i, sign in enumerate(working_memory, 24):
            body_mark = "【身】" if sign.get('body', False) else ""
            chars = "、".join(sign.get('characters', [])) or "无"
            content += f"""#### {i}. {sign['id']} {body_mark}
- **签语**：{sign['text'][:60]}...
- **人物**：{chars} | **亮度**：{sign['brightness']:.2f}

"""
        
        content += f"""
---

## 昨日梦境

{yesterday_dream if yesterday_dream else "（尚无梦境记录）"}

---

## 当前主题分布

"""
        for theme, count in themes[:7]:
            content += f"- **{theme}**：{count}次\n"
        
        content += """
---

## 人物出现统计

"""
        for char, count in sorted_chars[:10]:
            content += f"- **{char}**：{count}次\n"
        
        # 写入文件
        with open(self.context_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📄 已更新上下文: {self.context_path}")
    
    # ==================== Living Companion 维护 ====================
    
    def update_companion_state(self):
        """Living Companion 认知状态夜间维护"""
        companion_state_path = self.project_path.parent / "living-companion" / "companion-state.json"
        
        if not companion_state_path.exists():
            print("   ⚠️ Living Companion 状态文件不存在")
            return
        
        try:
            with open(companion_state_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # 1. 重置模式库频率统计（每日衰减）
            pattern_library = state.get("cognitive_state", {}).get("memory_layer", {}).get("pattern_library", {})
            for pattern_name, pattern_data in pattern_library.items():
                freq = pattern_data.get("frequency", 0)
                if freq > 0:
                    # 每日衰减 20%，最低保持 1
                    new_freq = max(1, int(freq * 0.8))
                    pattern_data["frequency"] = new_freq
            
            # 2. 清理贡献历史（保留最近 50 条）
            contribution_history = state.get("cognitive_state", {}).get("action_layer", {}).get("contribution_history", [])
            if len(contribution_history) > 50:
                state["cognitive_state"]["action_layer"]["contribution_history"] = contribution_history[-50:]
                print(f"   已清理贡献历史: 保留最近 50 条")
            
            # 3. 更新最后维护时间
            state["last_updated"] = datetime.now().isoformat()
            
            # 4. 同步学习状态中的成功/失败模式（保留最近 20 个）
            learning_state = state.get("learning_state", {})
            for key in ["successful_patterns", "rejected_patterns"]:
                patterns = learning_state.get(key, [])
                if len(patterns) > 20:
                    learning_state[key] = patterns[-20:]
            
            # 保存更新后的状态
            with open(companion_state_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            
            print(f"   ✅ Companion 状态已维护")
            
        except Exception as e:
            print(f"   ⚠️ Companion 状态维护失败: {e}")
    
    # ==================== Living Forest 维护 ====================

    def extract_work_summary(self, sessions):
        """
        从对话中提取工作摘要（Living Forest 变更）
        返回: {'new': 0, 'archived': 0, 'merged': 0, 'moved': 0, 'changes': []}
        """
        summary = {
            'new': 0,
            'archived': 0,
            'merged': 0,
            'moved': 0,
            'has_changes': False,
            'changes': []
        }
        
        # 关键词模式
        patterns = {
            'new': ['新建', '创建', '初始化', '立项', '新增', '启动'],
            'archived': ['归档', '废弃', '删除', '完成', '结束', '关闭'],
            'merged': ['合并', '整合', '统一', '融合'],
            'moved': ['移动', '迁移', '重命名', '更名', '改名']
        }
        
        for session in sessions:
            content = session.get('content', '')
            if not content:
                continue
            
            for change_type, keywords in patterns.items():
                for kw in keywords:
                    if kw in content:
                        summary[change_type] += 1
                        summary['has_changes'] = True
                        # 提取项目名称（简单启发式：关键词后5-20字）
                        idx = content.find(kw)
                        if idx >= 0:
                            project_name = content[idx:idx+30].strip()
                            summary['changes'].append({
                                'type': change_type,
                                'keyword': kw,
                                'context': project_name
                            })
                        break  # 每个session只算一次同类变更
        
        return summary
    
    def scan_and_add_projects(self):
        """
        自动扫描工作目录，发现新项目并添加到索引
        扫描路径：~/Projects/ 或 ~/workspace/ 等常见项目目录
        """
        index_path = self.project_path.parent / "living-forest" / "index" / "active-index.json"
        
        # 加载现有索引
        if index_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
                index = json.load(f)
        else:
            index = {"meta": {"version": "v1", "project_count": 0}, "projects": []}
        
        existing_paths = {p.get("path", "") for p in index.get("projects", [])}
        new_projects = []
        
        # 扫描常见项目目录
        scan_dirs = [
            Path.home() / "Projects",
            Path.home() / "workspace",
            Path.home() / "work",
            Path.home() / "Code",
        ]
        
        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue
            
            for item in scan_dir.iterdir():
                if not item.is_dir():
                    continue
                
                # 跳过隐藏目录和常见非项目目录
                if item.name.startswith('.') or item.name in ['node_modules', '__pycache__', 'venv', '.git']:
                    continue
                
                # 检查是否已存在
                item_path = str(item)
                if item_path in existing_paths:
                    continue
                
                # 判断是否为项目目录（包含常见项目标记）
                is_project = self._is_project_directory(item)
                
                if is_project:
                    new_project = {
                        "name": item.name,
                        "path": item_path,
                        "keywords": [item.name.lower().replace('-', ' ').replace('_', ' ')],
                        "status": "active",
                        "priority": "medium",
                        "last_active": datetime.now().isoformat(),
                        "auto_detected": True
                    }
                    new_projects.append(new_project)
                    index["projects"].append(new_project)
        
        # 如果有新项目，保存索引
        if new_projects:
            index["meta"]["project_count"] = len(index["projects"])
            index["meta"]["last_updated"] = datetime.now().isoformat()
            
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index, f, ensure_ascii=False, indent=2)
            
            print(f"   🔍 自动发现 {len(new_projects)} 个新项目:")
            for p in new_projects:
                print(f"      + {p['name']}")
        else:
            print("   🔍 未发现新项目")
        
        return len(new_projects)
    
    def _is_project_directory(self, path):
        """判断目录是否为项目目录"""
        # 检查常见项目标记文件
        project_markers = [
            '.git',           # Git 仓库
            'README.md',      # 项目说明
            'package.json',   # Node.js 项目
            'requirements.txt', # Python 项目
            'Cargo.toml',     # Rust 项目
            'pom.xml',        # Maven 项目
            'build.gradle',   # Gradle 项目
            'Makefile',       # Makefile 项目
            'CMakeLists.txt', # CMake 项目
            '_tree.json',     # Living Forest 标记
            'pyproject.toml', # Python 现代项目
            'setup.py',       # Python 传统项目
        ]
        
        for marker in project_markers:
            if (path / marker).exists():
                return True
        
        # 检查是否包含源代码文件（简单启发式）
        source_extensions = ['.py', '.js', '.ts', '.java', '.rs', '.go', '.cpp', '.c', '.h']
        file_count = 0
        for ext in source_extensions:
            if list(path.glob(f'*{ext}')):
                file_count += 1
                if file_count >= 2:  # 包含至少两种源文件，更可能是项目
                    return True
        
        return False
    
    def update_living_forest_index(self, work_summary):
        """根据工作摘要更新 Living Forest 索引"""
        index_path = self.project_path.parent / "living-forest" / "index" / "active-index.json"
        
        if not index_path.exists():
            print(f"   ⚠️ Living Forest 索引不存在: {index_path}")
            return
        
        with open(index_path, 'r', encoding='utf-8') as f:
            index = json.load(f)
        
        # 更新活跃项目的 last_active
        for proj in index.get('projects', []):
            if proj.get('status') in ['active', 'research', 'draft']:
                proj['last_active'] = datetime.now().isoformat()
        
        # 如果有归档操作，自动处理（简化版：根据对话关键词推断）
        for change in work_summary.get('changes', []):
            if change['type'] == 'archived':
                # 查找匹配的项目并归档
                for proj in index.get('projects', []):
                    if proj['name'] in change['context'] and proj.get('status') == 'active':
                        proj['status'] = 'archived'
                        proj['archived_at'] = datetime.now().isoformat()
                        proj['brief'] = f"于{datetime.now().strftime('%Y-%m-%d')}归档"
                        print(f"   📦 自动归档项目: {proj['name']}")
                        break
        
        # 更新 meta
        active_count = len([p for p in index['projects'] if p.get('status') in ['active', 'research', 'draft']])
        archived_count = len([p for p in index['projects'] if p.get('status') in ['archived', 'done']])
        index['meta']['active_count'] = active_count
        index['meta']['archived_count'] = archived_count
        index['meta']['project_count'] = len(index['projects'])
        index['meta']['last_updated'] = datetime.now().isoformat()
        
        # 保存
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ Living Forest 索引已更新: {active_count}活跃, {archived_count}归档")
    
    def run(self):
        """运行完整夜间流程"""
        print("=" * 60)
        print("🌙 Living Dream - 夜间完整流程")
        print("=" * 60)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"初始签数: {len(self.data['signs'])}")
        print()
        
        # Step 1: 从昨日 session 提取高光时刻
        print("【Step 1/7】读取昨日 sessions...")
        sessions = self.extract_daily_sessions()
        
        # Step 2: 生成新签
        print("【Step 2/7】提取高情绪时刻并生成新签...")
        moments = self.extract_high_emotion_moments(sessions)
        new_signs = self.add_new_signs(moments)
        
        # Step 3: 自然衰减
        print("【Step 3/7】应用自然衰减...")
        self.apply_decay()
        
        # Step 4: 遗忘机制
        print("【Step 4/7】遗忘低亮度签...")
        deleted = self.forget_signs()
        
        # Step 5: 抽签并生成梦境
        print("【Step 5/7】抽签并生成梦境...")
        selected, count = self.draw_lots()
        dream = self.fuse_dream(selected)
        
        if dream:
            self.data['dreams'].append({
                'timestamp': datetime.now().isoformat(),
                'dream': dream,
                'signs': [s['id'] for s in selected],
                'sign_count': len(selected)
            })
            print(f"   梦境: {dream}")
        
        # Step 6: 更新上下文
        print("【Step 6/7】更新灵魂上下文...")
        self.update_context()
        
        # Step 7: 扫描并添加新项目 + 智能维护 Living Forest
        print("【Step 7/7】Living Forest 智能维护...")
        # 7a: 扫描发现新项目
        new_projects = self.scan_and_add_projects()
        # 7b: 从对话提取工作变更
        work_summary = self.extract_work_summary(sessions)
        if work_summary['has_changes']:
            print(f"   检测到工作变更: 新增{work_summary['new']}, 归档{work_summary['archived']}, 合并{work_summary['merged']}, 移动{work_summary['moved']}")
            self.update_living_forest_index(work_summary)
        else:
            print("   无项目变更，仅更新活跃项目时间戳")
            # 仍然更新时间戳
            self.update_living_forest_index(work_summary)
        
        # Step 8: Living Companion 认知状态维护
        print("【Step 8】Living Companion 认知状态维护...")
        self.update_companion_state()
        
        # 保存数据
        self._save_db()
        
        # 完成报告
        print()
        print("=" * 60)
        print("✅ 夜间流程完成")
        print("=" * 60)
        print(f"新增签: {new_signs}")
        print(f"遗忘签: {deleted}")
        print(f"当前总签数: {len(self.data['signs'])}")
        print(f"昨日梦境: {dream if dream else '无'}")
        print(f"新项目: {new_projects}个")
        if work_summary['has_changes']:
            print(f"工作变更: {len(work_summary['changes'])}项")
        print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Living Dream 夜间维护流程')
    parser.add_argument('--init', action='store_true', help='初始化签筒数据库')
    parser.add_argument('--data-dir', type=str, default=None, 
                        help='数据目录路径（默认使用代码所在目录）')
    args = parser.parse_args()
    
    # 使用指定的数据目录
    routine = LivingDreamNightRoutine(data_dir=args.data_dir)
    
    print(f"📂 数据目录: {routine.data_path}")
    print(f"📂 代码目录: {routine.project_path}")
    print()
    
    if args.init:
        # 初始化模式：创建空数据库
        if routine.db_path.exists():
            print(f"⚠️ 签筒数据库已存在: {routine.db_path}")
            print("如需重新初始化，请先删除该文件")
        else:
            routine.data = {"signs": [], "dreams": []}
            routine._save_db()
            print(f"✅ 已初始化签筒数据库: {routine.db_path}")
    else:
        # 正常运行夜间流程
        routine.run()
