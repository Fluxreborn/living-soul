#!/usr/bin/env python3
"""
Living Companion - 社交情境导入模块

支持从多种来源导入社交关系信息：
- 飞书会话导出
- 微信聊天记录  
- 会议记录（Markdown/Notion）

流程：上传 → 解析 → 候选摘要 → 用户确认 → 入库
"""

import json
import re
from datetime import datetime
from pathlib import Path


class SocialContextImporter:
    """社交情境导入器"""
    
    def __init__(self):
        self.project_path = Path("~/Projects/livingsoul").expanduser()
        self.state_path = self.project_path / "living-companion/companion-state.json"
        self.forest_path = self.project_path / "living-forest/index/active-index.json"
        
    def _load_state(self):
        """加载Companion状态"""
        with open(self.state_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_state(self, state):
        """保存Companion状态"""
        with open(self.state_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    
    def parse_feishu_export(self, file_path):
        """
        解析飞书会话导出文件
        
        支持格式：JSON导出
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        messages = data.get("messages", [])
        
        # 提取参与者
        participants = {}
        for msg in messages:
            sender = msg.get("sender", "")
            if sender not in participants:
                participants[sender] = {
                    "message_count": 0,
                    "first_message": None,
                    "key_quotes": []
                }
            participants[sender]["message_count"] += 1
            
            if not participants[sender]["first_message"]:
                participants[sender]["first_message"] = msg.get("timestamp")
            
            # 提取关键引用（带情绪信号的）
            content = msg.get("content", "")
            if self._has_emotion_signal(content):
                participants[sender]["key_quotes"].append({
                    "timestamp": msg.get("timestamp"),
                    "content": content[:100],
                    "emotion": self._detect_emotion(content)
                })
        
        # 生成候选关系
        candidates = []
        for name, info in participants.items():
            if info["message_count"] < 3:  # 过滤只发了几条消息的
                continue
                
            candidate = {
                "name": name,
                "inferred_role": self._infer_role(name, info),
                "message_count": info["message_count"],
                "interaction_span": info["first_message"],
                "key_quotes": info["key_quotes"][:3],  # 最多3个关键引用
                "communication_pattern": self._analyze_pattern(info["key_quotes"]),
                "source_file": str(file_path)
            }
            candidates.append(candidate)
        
        return candidates
    
    def parse_wechat_export(self, file_path):
        """
        解析微信聊天记录导出
        
        支持格式：文本导出
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析微信格式：[时间] 发送者\n消息内容\n\n
        pattern = r'\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\]\s+([^\n]+)\n([^\n]+)'
        matches = re.findall(pattern, content)
        
        participants = {}
        for timestamp, sender, message in matches:
            if sender not in participants:
                participants[sender] = {
                    "message_count": 0,
                    "first_message": timestamp,
                    "key_quotes": []
                }
            participants[sender]["message_count"] += 1
            
            if self._has_emotion_signal(message):
                participants[sender]["key_quotes"].append({
                    "timestamp": timestamp,
                    "content": message[:100],
                    "emotion": self._detect_emotion(message)
                })
        
        candidates = []
        for name, info in participants.items():
            if info["message_count"] < 3:
                continue
                
            candidate = {
                "name": name,
                "inferred_role": "未知",
                "message_count": info["message_count"],
                "interaction_span": info["first_message"],
                "key_quotes": info["key_quotes"][:3],
                "communication_pattern": self._analyze_pattern(info["key_quotes"]),
                "source_file": str(file_path)
            }
            candidates.append(candidate)
        
        return candidates
    
    def parse_meeting_notes(self, file_path):
        """
        解析会议记录
        
        支持格式：Markdown
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取会议基本信息
        title_match = re.search(r'#\s+(.+)', content)
        title = title_match.group(1) if title_match else "未命名会议"
        
        date_match = re.search(r'时间[：:]\s*(\d{4}-\d{2}-\d{2})', content)
        date = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")
        
        participants_match = re.search(r'参与者[：:]\s*(.+)', content)
        participants = []
        if participants_match:
            participants = [p.strip() for p in participants_match.group(1).split('、')]
        
        # 提取关键结论和冲突点
        conclusions = re.findall(r'[\-\*]\s*(.+)', content)
        
        # 生成候选人（基于参与者列表）
        candidates = []
        for participant in participants:
            if not participant or participant == "你":
                continue
                
            # 从结论中提取该参与者的发言
            participant_quotes = []
            for conclusion in conclusions:
                if participant.split('（')[0] in conclusion:  # 匹配姓名部分
                    participant_quotes.append({
                        "content": conclusion,
                        "emotion": self._detect_emotion(conclusion)
                    })
            
            candidate = {
                "name": participant.split('（')[0],  # 去掉括号里的角色
                "inferred_role": self._extract_role(participant),
                "meeting_title": title,
                "meeting_date": date,
                "key_quotes": participant_quotes[:3],
                "communication_pattern": self._analyze_pattern(participant_quotes),
                "source_file": str(file_path)
            }
            candidates.append(candidate)
        
        return candidates
    
    def _has_emotion_signal(self, text):
        """检测是否包含情绪信号"""
        emotion_keywords = [
            "担心", "焦虑", "害怕", "紧张", "压力",
            "开心", "兴奋", "期待", "喜欢",
            "讨厌", "烦", "生气", "愤怒",
            "不知道", "迷茫", "困惑", "难"
        ]
        return any(kw in text for kw in emotion_keywords)
    
    def _detect_emotion(self, text):
        """检测情绪类型"""
        text = text.lower()
        
        if any(w in text for w in ["担心", "焦虑", "害怕", "紧张", "压力"]):
            return "concerned"
        if any(w in text for w in ["开心", "兴奋", "期待", "喜欢", "棒"]):
            return "positive"
        if any(w in text for w in ["讨厌", "烦", "生气", "愤怒", "不满"]):
            return "negative"
        if any(w in text for w in ["不知道", "迷茫", "困惑", "难", "不确定"]):
            return "uncertain"
        
        return "neutral"
    
    def _infer_role(self, name, info):
        """从名称推断角色"""
        # 简单的启发式规则
        if "技术" in name or "开发" in name or "后端" in name or "前端" in name:
            return "技术负责人"
        if "产品" in name or "PM" in name:
            return "产品负责人"
        if "运营" in name or "市场" in name:
            return "运营负责人"
        if "设计" in name or "UI" in name or "UX" in name:
            return "设计师"
        if "老板" in name or "总" in name or "经理" in name:
            return "管理层"
        
        return "协作者"
    
    def _extract_role(self, participant_str):
        """从参与者字符串提取角色"""
        role_match = re.search(r'[（(]([^)]+)[)）]', participant_str)
        if role_match:
            return role_match.group(1)
        return "未知"
    
    def _analyze_pattern(self, quotes):
        """分析沟通模式"""
        if not quotes:
            return "信息不足"
        
        emotions = [q.get("emotion", "neutral") for q in quotes]
        
        if "concerned" in emotions and "positive" not in emotions:
            return "直接表达担忧"
        if "positive" in emotions and "concerned" not in emotions:
            return "积极支持"
        if emotions.count("uncertain") > 1:
            return "倾向于保留意见"
        if "negative" in emotions:
            return "有明显抵触情绪"
        
        return "中立客观"
    
    def interactive_confirmation(self, candidates):
        """
        交互式确认流程
        
        返回用户确认后的关系列表
        """
        confirmed = []
        
        print("\n" + "=" * 60)
        print("📋 社交情境导入 - 候选摘要")
        print("=" * 60)
        
        for i, candidate in enumerate(candidates, 1):
            print(f"\n【候选人 {i}/{len(candidates)}】")
            print(f"姓名：{candidate['name']}")
            print(f"推断身份：{candidate['inferred_role']}")
            print(f"互动次数：{candidate['message_count'] if 'message_count' in candidate else '会议记录'}")
            print(f"沟通模式：{candidate['communication_pattern']}")
            
            if candidate['key_quotes']:
                print("关键引用：")
                for j, quote in enumerate(candidate['key_quotes'], 1):
                    print(f"  {j}. [{quote.get('emotion', 'neutral')}] {quote['content'][:60]}...")
            
            # 简化版：自动确认（实际使用时交互）
            confirmed.append({
                "confirmed": True,
                "candidate": candidate,
                "edited_role": candidate['inferred_role'],
                "user_notes": ""
            })
        
        return confirmed
    
    def save_to_state(self, confirmed_relations, project_name=None):
        """
        将确认的关系保存到 Companion 状态
        """
        state = self._load_state()
        
        if "social_context" not in state:
            state["social_context"] = {
                "enabled": True,
                "import_history": [],
                "relationships": [],
                "project_relations": {}
            }
        
        import_id = f"imp_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        import_record = {
            "import_id": import_id,
            "timestamp": datetime.now().isoformat(),
            "records_extracted": len(confirmed_relations),
            "user_confirmed": sum(1 for r in confirmed_relations if r["confirmed"]),
            "source_type": "mixed"
        }
        state["social_context"]["import_history"].append(import_record)
        
        # 保存关系
        for relation in confirmed_relations:
            if not relation["confirmed"]:
                continue
                
            candidate = relation["candidate"]
            
            rel_id = f"rel_{candidate['name'].lower().replace(' ', '_')}_{import_id[-6:]}"
            
            rel_record = {
                "id": rel_id,
                "name": candidate["name"],
                "title": relation["edited_role"],
                "source": "imported",
                "import_id": import_id,
                "first_seen": candidate.get("interaction_span") or candidate.get("meeting_date"),
                "last_updated": datetime.now().isoformat(),
                "communication_pattern": candidate["communication_pattern"],
                "key_events": [
                    {
                        "date": q.get("timestamp", datetime.now().strftime("%Y-%m-%d")),
                        "event": q["content"][:80],
                        "sentiment": q.get("emotion", "neutral"),
                        "quote": q["content"][:100]
                    }
                    for q in candidate.get("key_quotes", [])
                ],
                "current_status": candidate["communication_pattern"],
                "projects_involved": [project_name] if project_name else [],
                "user_notes": relation["user_notes"],
                "privacy_level": "project_only"
            }
            
            state["social_context"]["relationships"].append(rel_record)
        
        # 关联到项目
        if project_name:
            if project_name not in state["social_context"]["project_relations"]:
                state["social_context"]["project_relations"][project_name] = {
                    "stakeholders": [],
                    "current_blocker": None,
                    "next_alignment_needed": None
                }
            
            for relation in confirmed_relations:
                if relation["confirmed"]:
                    rel_id = f"rel_{relation['candidate']['name'].lower().replace(' ', '_')}_{import_id[-6:]}"
                    if rel_id not in state["social_context"]["project_relations"][project_name]["stakeholders"]:
                        state["social_context"]["project_relations"][project_name]["stakeholders"].append(rel_id)
        
        self._save_state(state)
        
        print(f"\n✅ 已保存 {import_record['user_confirmed']} 个关系到 Companion 状态")
        print(f"   导入ID: {import_id}")
        
        return import_id
    
    def import_file(self, file_path, source_type="auto", project_name=None, dry_run=False):
        """
        主导入函数
        
        Args:
            file_path: 导入文件路径
            source_type: 源类型 (feishu/wechat/meeting/auto)
            project_name: 关联的项目名称
            dry_run: 是否只预览不保存
        
        Returns:
            导入结果摘要
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {"error": f"文件不存在: {file_path}"}
        
        # 自动检测源类型
        if source_type == "auto":
            if file_path.suffix == ".json":
                source_type = "feishu"
            elif "会议" in file_path.name or file_path.suffix == ".md":
                source_type = "meeting"
            else:
                source_type = "wechat"
        
        # 解析文件
        print(f"📂 正在解析 {source_type} 格式: {file_path.name}")
        
        try:
            if source_type == "feishu":
                candidates = self.parse_feishu_export(file_path)
            elif source_type == "wechat":
                candidates = self.parse_wechat_export(file_path)
            elif source_type == "meeting":
                candidates = self.parse_meeting_notes(file_path)
            else:
                return {"error": f"不支持的源类型: {source_type}"}
        
        except Exception as e:
            return {"error": f"解析失败: {str(e)}"}
        
        if not candidates:
            return {"message": "未检测到有效关系候选人"}
        
        print(f"✓ 发现 {len(candidates)} 个候选人")
        
        # 交互式确认
        confirmed = self.interactive_confirmation(candidates)
        
        if dry_run:
            print("\n⏸️ 预览模式，未保存")
            return {
                "dry_run": True,
                "candidates_found": len(candidates),
                "would_confirm": sum(1 for r in confirmed if r["confirmed"])
            }
        
        # 保存到状态
        import_id = self.save_to_state(confirmed, project_name)
        
        return {
            "success": True,
            "import_id": import_id,
            "candidates_found": len(candidates),
            "confirmed": sum(1 for r in confirmed if r["confirmed"]),
            "project": project_name
        }


if __name__ == "__main__":
    import sys
    
    importer = SocialContextImporter()
    
    if len(sys.argv) < 2:
        print("用法: python3 import_social.py <文件路径> [--dry-run]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    dry_run = "--dry-run" in sys.argv
    
    result = importer.import_file(file_path, dry_run=dry_run)
    
    print("\n" + "=" * 60)
    print("📊 导入结果")
    print("=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2))
