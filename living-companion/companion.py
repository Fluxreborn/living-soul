#!/usr/bin/env python3
"""
Living Companion - 合伙人级AI陪伴系统

核心原则：
1. 基于Dream的记忆形成独立判断
2. 在关键时刻主动贡献认知价值
3. 与用户共同成长，双向塑造

不是秘书，不是工具，是认知合伙人。
"""

import json
import re
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher


class LivingCompanion:
    """
    Living Companion 核心类
    
    职责：
    - 从Dream读取记忆，形成模式识别
    - 从Forest读取项目状态
    - 判断何时主动贡献
    - 生成合伙人级别的表达
    """
    
    def __init__(self):
        self.project_path = Path("~/Projects/livingsoul").expanduser()
        self.state_path = self.project_path / "living-companion/companion-state.json"
        self.dream_path = self.project_path / "living-dream/living-dream-memory.json"
        self.forest_path = self.project_path / "living-forest/index/active-index.json"
        
        # 加载状态
        self.state = self._load_state()
        
    def _load_state(self):
        """加载Companion认知状态"""
        if not self.state_path.exists():
            return self._init_state()
        
        with open(self.state_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _init_state(self):
        """初始化默认状态"""
        return {
            "version": "0.1.0",
            "last_updated": datetime.now().isoformat(),
            "cognitive_state": {
                "memory_layer": {"highlights": [], "pattern_library": {}},
                "judgment_layer": {"current_hypothesis": None, "confidence": 0.0},
                "action_layer": {"strategy": "observe", "last_contribution": None}
            }
        }
    
    def _save_state(self):
        """保存状态"""
        self.state["last_updated"] = datetime.now().isoformat()
        with open(self.state_path, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
    
    def load_dream_signs(self, min_brightness=0.7):
        """
        从Living Dream加载高亮签名
        
        返回亮度 > threshold 的签名列表
        """
        if not self.dream_path.exists():
            return []
        
        with open(self.dream_path, 'r', encoding='utf-8') as f:
            dream_data = json.load(f)
        
        signs = dream_data.get("signs", [])
        # 筛选高亮签名
        highlights = [s for s in signs if s.get("brightness", 0) >= min_brightness]
        # 按亮度排序
        highlights.sort(key=lambda x: x.get("brightness", 0), reverse=True)
        
        return highlights[:10]  # 取前10个最亮的
    
    def load_forest_projects(self):
        """
        从Living Forest加载活跃项目
        
        返回当前进行中的项目列表
        """
        if not self.forest_path.exists():
            return []
        
        with open(self.forest_path, 'r', encoding='utf-8') as f:
            forest_data = json.load(f)
        
        projects = forest_data.get("projects", [])
        active = [p for p in projects if p.get("status") in ["active", "research", "draft"]]
        
        return active
    
    def extract_patterns(self, highlights, current_topic=None):
        """
        从签名中提取跨时间模式
        
        算法：
        1. 关键词交集分析
        2. 主题聚类
        3. 情绪演化追踪
        """
        patterns = []
        
        # 获取模式库定义
        pattern_lib = self.state.get("cognitive_state", {}).get("memory_layer", {}).get("pattern_library", {})
        
        for pattern_name, pattern_def in pattern_lib.items():
            triggers = pattern_def.get("triggers", [])
            matches = []
            
            for sign in highlights:
                text = sign.get("text", "") + " " + sign.get("event", "")
                # 检查触发词
                if any(t in text for t in triggers):
                    matches.append({
                        "sign_id": sign.get("id"),
                        "text": sign.get("text", "")[:50],
                        "brightness": sign.get("brightness"),
                        "emotion": sign.get("emotion", "")
                    })
            
            if len(matches) >= 2:  # 至少2次出现才算模式
                patterns.append({
                    "name": pattern_name,
                    "description": pattern_def.get("description"),
                    "matches": matches,
                    "strength": len(matches) * sum(m["brightness"] for m in matches) / len(matches)
                })
        
        # 按强度排序
        patterns.sort(key=lambda x: x["strength"], reverse=True)
        return patterns[:3]  # 返回最强的3个模式
    
    def calculate_relevance(self, patterns, current_topic):
        """
        计算模式与当前话题的相关性
        
        0-1之间，越高越相关
        """
        if not current_topic or not patterns:
            return 0.5
        
        # 简单关键词匹配
        topic_words = set(re.findall(r'\w+', current_topic.lower()))
        
        max_relevance = 0
        for pattern in patterns:
            pattern_words = set(re.findall(r'\w+', pattern["description"].lower()))
            if pattern.get("matches"):
                for match in pattern["matches"]:
                    match_words = set(re.findall(r'\w+', match["text"].lower()))
                    pattern_words.update(match_words)
            
            # Jaccard相似度
            intersection = topic_words & pattern_words
            union = topic_words | pattern_words
            relevance = len(intersection) / len(union) if union else 0
            max_relevance = max(max_relevance, relevance)
        
        return min(1.0, max_relevance * 2)  # 放大信号
    
    def calculate_novelty(self, patterns):
        """
        计算模式的新颖性
        
        基于上次是否提及
        """
        last_contribution = self.state.get("cognitive_state", {}).get("action_layer", {}).get("last_contribution", {})
        last_patterns = last_contribution.get("patterns", [])
        
        if not last_patterns:
            return 1.0  # 全新
        
        # 检查重复
        current_names = {p["name"] for p in patterns}
        last_names = set(last_patterns)
        
        overlap = current_names & last_names
        novelty = 1.0 - (len(overlap) / len(current_names)) if current_names else 0
        
        return novelty
    
    def calculate_actionability(self, patterns):
        """
        计算可行动性
        
        模式是否指向具体决策点
        """
        actionable_keywords = ["卡住", "停滞", "重复", "焦虑", "风险", "机会", "转向"]
        
        score = 0.5  # 基础分
        
        for pattern in patterns:
            desc = pattern.get("description", "")
            if any(kw in desc for kw in actionable_keywords):
                score += 0.2
            
            for match in pattern.get("matches", []):
                text = match.get("text", "")
                if any(kw in text for kw in actionable_keywords):
                    score += 0.1
        
        return min(1.0, score)
    
    def should_contribute(self, current_topic=None, turn_count=0):
        """
        判断是否该主动贡献
        
        返回：(should_contribute, quality_score, reasoning)
        """
        # 加载数据
        highlights = self.load_dream_signs()
        patterns = self.extract_patterns(highlights, current_topic)
        
        if not patterns:
            return False, 0.0, "无高价值模式可贡献"
        
        # 计算质量分数
        relevance = self.calculate_relevance(patterns, current_topic)
        novelty = self.calculate_novelty(patterns)
        actionability = self.calculate_actionability(patterns)
        
        weights = self.state.get("contribution_thresholds", {})
        w_rel = weights.get("relevance_weight", 0.4)
        w_nov = weights.get("novelty_weight", 0.3)
        w_act = weights.get("actionability_weight", 0.3)
        
        quality_score = relevance * w_rel + novelty * w_nov + actionability * w_act
        
        threshold = weights.get("quality_score", 0.6)
        
        # 额外条件
        reasoning_parts = [
            f"相关性={relevance:.2f}",
            f"新颖性={novelty:.2f}",
            f"可行动性={actionability:.2f}",
            f"总分={quality_score:.2f} (阈值{threshold})"
        ]
        
        # 检查沉默期
        last_spoke = self.state.get("session_context", {}).get("companion_last_spoke")
        silence_threshold = weights.get("silence_after_contribution", 3)
        
        if last_spoke and turn_count - last_spoke < silence_threshold:
            return False, quality_score, f"刚贡献过，需沉默{silence_threshold}轮"
        
        should = quality_score >= threshold
        reasoning = "; ".join(reasoning_parts)
        
        return should, quality_score, reasoning
    
    def generate_contribution(self, patterns, current_topic=None):
        """
        生成合伙人级别的贡献内容
        
        模板：
        "我想起 [记忆]。 [我的判断]。 [我的立场/建议]。 [开放性结尾]"
        """
        if not patterns:
            return None
        
        # 选择最强模式
        top_pattern = patterns[0]
        matches = top_pattern.get("matches", [])
        
        if not matches:
            return None
        
        # 构建记忆引用
        memory_refs = []
        for m in matches[:2]:  # 引用最近的2个实例
            sign_text = m.get("text", "")[:30]
            memory_refs.append(f"{m['sign_id']}：{sign_text}...")
        
        memory_part = f"我想起 {top_pattern['description']}。"
        if memory_refs:
            memory_part += f"（具体在 {', '.join(memory_refs)}）"
        
        # 构建判断
        judgment_templates = {
            "naming_anxiety": "我觉得我们在这里有重复的模式。",
            "concept_stacking": "我意识到我可能又在用概念逃避具体。",
            "quality_migration": "我看到质地思维在迁移，这是同一个底层模式吗？"
        }
        
        judgment = judgment_templates.get(
            top_pattern["name"], 
            f"我注意到 {top_pattern['description']} 在重复。"
        )
        
        # 构建立场/建议
        stance_templates = {
            "naming_anxiety": "我的立场：先不急着定名字，让概念再沉淀。",
            "concept_stacking": "我的立场：暂停理论，先做最小可行测试。",
            "quality_migration": "我的立场：观察这个迁移是否有价值，还是惯性。"
        }
        
        stance = stance_templates.get(
            top_pattern["name"],
            "我的立场：这个模式值得关注，但决策权在你。"
        )
        
        # 开放性结尾
        endings = [
            "你觉得呢？",
            "这是我看到的，但我可能错了。",
            "这个判断对你有用吗？"
        ]
        ending = endings[hash(top_pattern["name"]) % len(endings)]
        
        contribution = f"{memory_part}\n\n{judgment}\n\n{stance}\n\n{ending}"
        
        return {
            "content": contribution,
            "pattern": top_pattern["name"],
            "quality_score": top_pattern.get("strength", 0),
            "timestamp": datetime.now().isoformat()
        }
    
    def update_after_contribution(self, contribution, user_response=None):
        """
        贡献后更新状态
        
        记录反馈，调整策略
        """
        action_layer = self.state["cognitive_state"]["action_layer"]
        
        action_layer["last_contribution"] = {
            "type": "pattern_surfacing",
            "content": contribution["content"][:100],
            "pattern": contribution["pattern"],
            "timestamp": contribution["timestamp"],
            "user_response": user_response
        }
        
        action_layer["contribution_history"].append({
            "pattern": contribution["pattern"],
            "timestamp": contribution["timestamp"],
            "user_response_type": self._classify_response(user_response)
        })
        
        # 更新策略
        if user_response:
            response_type = self._classify_response(user_response)
            if response_type in ["adoption", "engagement"]:
                action_layer["strategy"] = "continue"
            elif response_type == "rejection":
                action_layer["strategy"] = "pause"
            else:
                action_layer["strategy"] = "observe"
        
        self._save_state()
    
    def _classify_response(self, response):
        """简单分类用户回应"""
        if not response:
            return "none"
        
        positive = ["对", "是的", "好", "同意", "采纳"]
        negative = ["不", "错", "不对", "不是"]
        engagement = ["为什么", "怎么", "如果", "但是"]
        
        for p in positive:
            if p in response:
                return "adoption"
        for n in negative:
            if n in response:
                return "rejection"
        for e in engagement:
            if e in response:
                return "engagement"
        
        return "neutral"
    
    def detect_emergency_signals(self, user_message):
        """
        检测紧急触发信号
        
        返回: (is_emergency, emergency_type, intensity)
        """
        if not user_message:
            return False, None, 0
        
        text = user_message.lower()
        
        # 1. 强烈情绪检测
        emotion_signals = {
            "焦虑": ["焦虑", "担心", "害怕", "恐惧", "压力", "受不了"],
            "愤怒": ["愤怒", "生气", "讨厌", "恨", "烦死", "受够了"],
            "兴奋": ["兴奋", "激动", "太棒", "必须", "绝对", "一定要"],
            "迷茫": ["迷茫", "不知道", "怎么办", "无助", "迷失"]
        }
        
        detected_emotions = []
        for emotion, keywords in emotion_signals.items():
            if any(kw in text for kw in keywords):
                detected_emotions.append(emotion)
        
        # 标点符号密度（感叹号、问号、省略号）
        punct_count = text.count('！') + text.count('?') + text.count('？') + text.count('…') + text.count('~')
        punct_density = punct_count / max(len(text), 1)
        
        # 2. 重大决策检测
        decision_signals = {
            "关键选择": ["选择", "决定", "抉择", "选a还是b", "要不要", "该不该"],
            "时间压力": ["今天", "马上", "立刻", " deadline", "来不及了", "最后机会"],
            "不可逆": ["无法回头", "放弃", "退出", "终止", "结束", "重新开始"],
            "高风险": ["风险", "赌注", "全部", "孤注一掷", "背水一战"]
        }
        
        detected_decisions = []
        for decision_type, keywords in decision_signals.items():
            if any(kw in text for kw in keywords):
                detected_decisions.append(decision_type)
        
        # 计算紧急强度
        intensity = 0
        emergency_type = None
        
        if detected_emotions:
            intensity += len(detected_emotions) * 0.3
            emergency_type = "强烈情绪"
        
        if detected_decisions:
            intensity += len(detected_decisions) * 0.4
            emergency_type = "重大决策" if not emergency_type else "情绪+决策"
        
        if punct_density > 0.1:  # 标点密度高
            intensity += 0.2
        
        # 全大写（ shouting ）
        if any(c.isupper() for c in user_message) and len(user_message) > 10:
            upper_ratio = sum(1 for c in user_message if c.isupper()) / len(user_message)
            if upper_ratio > 0.5:
                intensity += 0.2
                emergency_type = emergency_type or "强烈情绪"
        
        is_emergency = intensity >= 0.5
        
        return is_emergency, emergency_type, min(1.0, intensity)
    
    def find_similar_situations(self, emergency_type, user_message):
        """
        从 Dream 中寻找类似情境
        
        基于情绪匹配或主题匹配
        """
        highlights = self.load_dream_signs(min_brightness=0.5)
        
        similar = []
        
        # 情绪匹配
        emotion_keywords = {
            "焦虑": ["焦虑", "担心", "呼吸", "紧张"],
            "愤怒": ["愤怒", "生气", "钢筋", "强加"],
            "兴奋": ["兴奋", "期待", "喜悦", "发现"],
            "迷茫": ["迷茫", "不知道", "选择", "灵魂"]
        }
        
        # 提取用户消息中的情绪关键词
        user_emotion_words = []
        for emotion, keywords in emotion_keywords.items():
            if any(kw in user_message.lower() for kw in keywords):
                user_emotion_words.extend(keywords)
        
        for sign in highlights:
            sign_text = sign.get("text", "") + " " + sign.get("event", "")
            sign_emotion = sign.get("emotion", "")
            
            # 匹配度计算
            match_score = 0
            
            # 情绪词匹配
            for word in user_emotion_words:
                if word in sign_text.lower():
                    match_score += 0.2
            
            # 情绪标签匹配
            if emergency_type and emergency_type in sign_emotion:
                match_score += 0.3
            
            # 身体感匹配（强烈情绪通常伴随身体感）
            if sign.get("body") and emergency_type == "强烈情绪":
                match_score += 0.2
            
            if match_score > 0.3:
                similar.append({
                    "sign": sign,
                    "match_score": match_score,
                    "relevance": "情绪共鸣" if match_score > 0.5 else "情境相似"
                })
        
        # 按匹配度排序
        similar.sort(key=lambda x: x["match_score"], reverse=True)
        return similar[:3]  # 返回最相似的3个
    
    def generate_deep_analysis(self, emergency_type, intensity, similar_situations, user_message):
        """
        生成深度分析报告
        
        结构：
        1. 情绪/情境识别
        2. 历史参照（类似情境）
        3. 模式分析
        4. 可选方向（不替你做决定）
        """
        parts = []
        
        # 1. 识别声明
        intensity_desc = "强烈" if intensity > 0.8 else "明显"
        parts.append(f"我检测到你有{intensity_desc}的{emergency_type}信号。")
        
        # 2. 历史参照
        if similar_situations:
            parts.append("\n我想起类似的情境：")
            for i, sim in enumerate(similar_situations[:2], 1):
                sign = sim["sign"]
                text = sign.get("text", "")[:40]
                parts.append(f"  {i}. {sign['id']}: {text}... ({sim['relevance']})")
        
        # 3. 模式分析
        if similar_situations:
            patterns = []
            for sim in similar_situations:
                emotion = sim["sign"].get("emotion", "")
                if emotion and emotion not in patterns:
                    patterns.append(emotion)
            
            if patterns:
                parts.append(f"\n这些时刻的共同情绪：{', '.join(patterns)}")
        
        # 4. 可选方向（开放式，不直接建议）
        parts.append("\n基于这些记忆，我看到几个可能的方向：")
        
        if emergency_type == "强烈情绪":
            parts.append("  - 先处理身体信号（呼吸、颈椎），再处理决策")
            parts.append("  - 回顾过去类似时刻，你是如何度过的？")
        elif emergency_type == "重大决策":
            parts.append("  - 把'必须现在决定'的压力，和'真正重要的因素'分开")
            parts.append("  - 如果无法回头，那现在的犹豫本身是不是信号？")
        else:
            parts.append("  - 情绪和信息，哪个在主导这个时刻？")
            parts.append("  - 24小时后，你会怎么看待这个决定？")
        
        # 5. 开放性结尾
        parts.append("\n我在这里，不是要替你决定，而是帮你看到这些模式。你想从哪个角度开始？")
        
        return "\n".join(parts)
    
    def run_cycle(self, current_topic=None, turn_count=0, min_brightness=0.6, 
                  user_message=None, force_emergency=False):
        """
        运行一个Companion周期（增强版，支持紧急模式）
        
        完整流程：
        1. 检测紧急信号
        2. 如果是紧急模式 → 深度分析
        3. 否则 → 常规质量评估
        """
        print("=" * 60)
        print("🤝 Living Companion - 运行周期")
        print("=" * 60)
        
        # 0. 检测紧急信号
        is_emergency = False
        emergency_type = None
        intensity = 0
        
        if user_message or force_emergency:
            is_emergency, emergency_type, intensity = self.detect_emergency_signals(user_message)
            
            if is_emergency or force_emergency:
                print(f"\n🚨 紧急模式激活！")
                print(f"   类型: {emergency_type or '强制触发'}")
                print(f"   强度: {intensity:.2f}")
                
                # 紧急模式：直接进入深度分析
                print("\n【Step 1】加载历史记忆...")
                similar = self.find_similar_situations(emergency_type, user_message or "")
                print(f"   找到 {len(similar)} 个类似情境")
                
                print("\n【Step 2】生成深度分析...")
                analysis = self.generate_deep_analysis(
                    emergency_type, intensity, similar, user_message or ""
                )
                
                print("\n" + "=" * 60)
                print("💬 Companion 深度分析：")
                print("=" * 60)
                print(analysis)
                print("=" * 60)
                
                # 更新状态
                self.update_after_contribution({
                    "content": analysis[:100],
                    "pattern": f"emergency_{emergency_type}",
                    "timestamp": datetime.now().isoformat(),
                    "quality_score": intensity
                }, user_response=None)
                
                return {
                    "content": analysis,
                    "pattern": f"emergency_{emergency_type}",
                    "quality_score": intensity,
                    "mode": "emergency",
                    "timestamp": datetime.now().isoformat()
                }
        
        # 常规模式（原有的逻辑）
        print("\n【Step 1】加载记忆...")
        highlights = self.load_dream_signs(min_brightness=min_brightness)
        print(f"  高亮签名: {len(highlights)} 个")
        
        projects = self.load_forest_projects()
        print(f"  活跃项目: {len(projects)} 个")
        
        # 2. 提取模式
        print("\n【Step 2】提取跨时间模式...")
        patterns = self.extract_patterns(highlights, current_topic)
        print(f"  识别模式: {len(patterns)} 个")
        for p in patterns:
            print(f"    - {p['name']}: 强度={p['strength']:.2f}, 匹配={len(p['matches'])}次")
        
        # 3. 判断是否贡献
        print("\n【Step 3】判断贡献时机...")
        should, score, reasoning = self.should_contribute(current_topic, turn_count)
        print(f"  质量分数: {score:.2f}")
        print(f"  判断理由: {reasoning}")
        print(f"  是否贡献: {'是' if should else '否'}")
        
        # 4. 生成内容
        if should:
            print("\n【Step 4】生成贡献内容...")
            contribution = self.generate_contribution(patterns, current_topic)
            if contribution:
                print(f"\n{'='*60}")
                print("💬 Companion 主动输出：")
                print("=" * 60)
                print(contribution["content"])
                print("=" * 60)
                
                # 更新状态
                self.update_after_contribution(contribution)
                
                return contribution
        
        print("\n【结果】静默观察，等待更佳时机")
        return None
        
        projects = self.load_forest_projects()
        print(f"  活跃项目: {len(projects)} 个")
        
        # 2. 提取模式
        print("\n【Step 2】提取跨时间模式...")
        patterns = self.extract_patterns(highlights, current_topic)
        print(f"  识别模式: {len(patterns)} 个")
        for p in patterns:
            print(f"    - {p['name']}: 强度={p['strength']:.2f}, 匹配={len(p['matches'])}次")
        
        # 3. 判断是否贡献
        print("\n【Step 3】判断贡献时机...")
        should, score, reasoning = self.should_contribute(current_topic, turn_count)
        print(f"  质量分数: {score:.2f}")
        print(f"  判断理由: {reasoning}")
        print(f"  是否贡献: {'是' if should else '否'}")
        
        # 4. 生成内容
        if should:
            print("\n【Step 4】生成贡献内容...")
            contribution = self.generate_contribution(patterns, current_topic)
            if contribution:
                print(f"\n{'='*60}")
                print("💬 Companion 主动输出：")
                print("=" * 60)
                print(contribution["content"])
                print("=" * 60)
                
                # 更新状态
                self.update_after_contribution(contribution)
                
                return contribution
        
        print("\n【结果】静默观察，等待更佳时机")
        return None


if __name__ == "__main__":
    # 测试运行
    companion = LivingCompanion()
    
    # 模拟当前话题
    current_topic = "Living Companion 模块设计"
    turn_count = 5
    
    result = companion.run_cycle(current_topic, turn_count)
    
    if result:
        print("\n✅ Companion 已主动贡献")
    else:
        print("\n⏸️ Companion 选择静默")
