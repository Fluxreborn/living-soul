#!/usr/bin/env python3
"""
Soul Memory 完整版 - v3.1 遗忘机制

新增：
- 亮度 < 0.1 直接删除
- 30天未使用（未点亮）直接删除
- 所有签都参与抽签（无过滤）
"""

import json
import random
import os
import re
import logging
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SoulMemoryError(Exception):
    """灵魂记忆系统自定义异常"""
    pass


class SoulMemorySystem:
    def __init__(self, db_path="./living-dream-memory.json", soul_context_path="./living-dream-context.md"):
        self.db_path = Path(db_path)
        self.soul_context_path = Path(soul_context_path)
        self.backup_path = self.db_path.with_suffix('.json.backup')
        self.data = self._load()
        
    def _load(self):
        """加载数据，带容错和备份恢复机制"""
        # 如果主文件不存在，尝试从备份恢复
        if not self.db_path.exists():
            if self.backup_path.exists():
                logger.warning(f"主文件不存在，从备份恢复: {self.backup_path}")
                try:
                    with open(self.backup_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    # 恢复主文件
                    self.db_path.write_text(
                        self.backup_path.read_text(encoding='utf-8'), 
                        encoding='utf-8'
                    )
                    logger.info("已从备份恢复主文件")
                    return self._validate_data(data)
                except Exception as e:
                    logger.error(f"备份恢复失败: {e}")
            
            logger.info("创建新的空数据库")
            return {"signs": [], "dreams": []}
        
        # 主文件存在，尝试加载
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self._validate_data(data)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}")
            return self._restore_from_backup()
            
        except PermissionError:
            logger.error(f"无权限读取文件: {self.db_path}")
            raise SoulMemoryError(f"权限不足，无法读取数据库: {self.db_path}")
            
        except Exception as e:
            logger.error(f"加载数据库时发生未知错误: {e}")
            return self._restore_from_backup()
    
    def _validate_data(self, data):
        """验证并修复数据结构"""
        if not isinstance(data, dict):
            logger.warning(f"数据格式错误（应为 dict，实际为 {type(data)}），重置为空数据库")
            return {"signs": [], "dreams": []}
        
        # 确保必需字段存在
        if "signs" not in data or not isinstance(data["signs"], list):
            logger.warning("缺少 'signs' 字段或格式错误，初始化为空列表")
            data["signs"] = []
        
        if "dreams" not in data or not isinstance(data["dreams"], list):
            logger.warning("缺少 'dreams' 字段或格式错误，初始化为空列表")
            data["dreams"] = []
        
        # 修复每个签的数据
        for i, sign in enumerate(data["signs"]):
            if not isinstance(sign, dict):
                logger.warning(f"第 {i} 条签格式错误，跳过")
                continue
                
            # 确保必需字段
            if "id" not in sign:
                sign["id"] = f"auto_{datetime.now().isoformat()}_{i}"
                logger.warning(f"签缺少 id，自动生成: {sign['id']}")
            
            if "text" not in sign:
                sign["text"] = ""
            
            # 修复浮点精度问题
            if "brightness" in sign:
                try:
                    sign["brightness"] = round(float(sign["brightness"]), 4)
                except (TypeError, ValueError):
                    sign["brightness"] = 0.5
            else:
                sign["brightness"] = 0.5
            
            # 确保时间字段存在
            now = datetime.now().isoformat()
            if "created_at" not in sign:
                sign["created_at"] = now
            if "last_used" not in sign:
                sign["last_used"] = sign.get("created_at", now)
        
        return data
    
    def _restore_from_backup(self):
        """从备份恢复数据"""
        if self.backup_path.exists():
            logger.info(f"尝试从备份恢复: {self.backup_path}")
            try:
                with open(self.backup_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info("备份恢复成功")
                return self._validate_data(data)
            except Exception as e:
                logger.error(f"备份恢复失败: {e}")
        
        logger.warning("无可用备份，返回空数据库")
        return {"signs": [], "dreams": []}
    
    def _save(self):
        """保存数据，带备份机制"""
        try:
            # 如果主文件存在，先创建备份
            if self.db_path.exists():
                try:
                    backup_content = self.db_path.read_text(encoding='utf-8')
                    self.backup_path.write_text(backup_content, encoding='utf-8')
                except Exception as e:
                    logger.warning(f"创建备份失败（将继续保存）: {e}")
            
            # 保存主文件
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
                
        except PermissionError:
            logger.error(f"无权限写入文件: {self.db_path}")
            raise SoulMemoryError(f"权限不足，无法保存数据库: {self.db_path}")
            
        except Exception as e:
            logger.error(f"保存数据库时发生错误: {e}")
            raise SoulMemoryError(f"保存失败: {e}")
    
    def add_sign(self, sign_id, text, time=None, scene=None, characters=None, 
                 event=None, emotion=None, intensity=0.5, body=False, brightness=0.5):
        """
        添加签到数据库 - 六维闪回结构
        """
        
        sign = {
            "id": sign_id,
            "text": text,
            "time": time or "",
            "scene": scene or "",
            "characters": characters or [],
            "event": event or "",
            "emotion": emotion or "",
            "emotion_intensity": intensity,
            "body": body,
            "brightness": brightness,
            "echo_count": 0,
            "fusion_count": 0,
            "resonance_count": 0,
            "last_used": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "last_resonance": None
        }
        
        # 回响检测（阈值0.5）
        self._check_echo(sign)
        
        self.data["signs"].append(sign)
        self._save()
        
        return sign_id
    
    def _text_similarity(self, text1, text2):
        """计算文本相似度"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _check_echo(self, new_sign, threshold=0.5):
        """检查新签是否触发旧签回响"""
        for sign in self.data["signs"]:
            similarity = self._text_similarity(new_sign["text"], sign["text"])
            if similarity > threshold and sign["id"] != new_sign.get("id"):
                old_bright = sign["brightness"]
                sign["brightness"] = min(0.95, sign["brightness"] * 1.30)
                sign["echo_count"] += 1
                sign["last_used"] = datetime.now().isoformat()
                print(f"   ↳ 回响触发: {sign['id']} {old_bright:.2f}→{sign['brightness']:.2f}")
    
    def check_resonance(self, context_text):
        """
        情境共鸣检测
        返回：多条共鸣时随机选择一条
        """
        resonances = []
        soul_core = self.get_soul_core()
        
        for sign in soul_core:
            similarity = self._text_similarity(context_text, sign["text"])
            if similarity > 0.2:
                resonances.append((sign, similarity))
        
        if not resonances:
            return None
        
        # 多条时随机选择一条
        selected = random.choice(resonances)
        sign, similarity = selected
        
        # 更新共鸣统计
        sign["resonance_count"] += 1
        sign["last_resonance"] = datetime.now().isoformat()
        
        # 使用强化 +5%
        old_bright = sign["brightness"]
        sign["brightness"] = min(0.95, sign["brightness"] + 0.05)
        
        print(f"   ↳ 情境共鸣: {sign['id']} (随机选择，相似度{similarity:.2f})")
        self._save()
        
        return sign
    
    def get_soul_core(self):
        """Soul级：亮度最高的23条"""
        sorted_signs = sorted(self.data["signs"], key=lambda x: x["brightness"], reverse=True)
        return sorted_signs[:23]
    
    def get_working_memory(self):
        """Working级：亮度其次的26条（不包括Soul级）"""
        sorted_signs = sorted(self.data["signs"], key=lambda x: x["brightness"], reverse=True)
        return sorted_signs[23:49]
    
    def apply_decay(self):
        """应用自然衰减（每晚5%）"""
        for sign in self.data["signs"]:
            sign["brightness"] *= 0.95
        
        self._save()
    
    def forget_signs(self):
        """
        遗忘机制：
        - 亮度 < 0.1 直接删除
        - 30天未使用直接删除
        """
        now = datetime.now()
        to_delete = []
        
        for sign in self.data["signs"]:
            # 检查亮度
            if sign["brightness"] < 0.1:
                to_delete.append((sign["id"], "亮度<0.1"))
                continue
            
            # 检查30天未使用
            last_used_str = sign.get("last_used") or sign.get("created_at")
            if last_used_str:
                last_used = datetime.fromisoformat(last_used_str.replace('Z', '+00:00').replace('+00:00', ''))
                days_since_used = (now - last_used).days
                if days_since_used > 30:
                    to_delete.append((sign["id"], f"30天未使用({days_since_used}天)"))
        
        # 执行删除
        deleted_count = 0
        for sign_id, reason in to_delete:
            self.data["signs"] = [s for s in self.data["signs"] if s["id"] != sign_id]
            print(f"   🗑️ 遗忘: {sign_id} ({reason})")
            deleted_count += 1
        
        if deleted_count > 0:
            self._save()
        
        return deleted_count
    
    def draw_lots(self):
        """
        抽签：所有签等几率抽取（修正：去掉亮度权重，避免素材过度富集）
        """
        total = sum(range(1, 50))
        probabilities = [(49 - i + 1) / total for i in range(1, 50)]
        
        n = random.choices(range(1, 50), weights=probabilities, k=1)[0]
        
        # 所有签都参与（无过滤）
        valid_signs = self.data["signs"]
        
        if not valid_signs:
            return [], 0
        
        # 修正：等几率抽取，不按亮度加权
        n = min(n, len(valid_signs))
        selected = random.sample(valid_signs, k=n)
        
        seen_ids = set()
        unique_selected = []
        now = datetime.now().isoformat()
        for s in selected:
            if s["id"] not in seen_ids:
                unique_selected.append(s)
                seen_ids.add(s["id"])
                # 天选之签：被抽中也算使用，更新 last_used
                s["last_used"] = now
        
        if unique_selected:
            self._save()
        
        return unique_selected, len(unique_selected)
    
    def fuse_signs(self, selected_signs):
        """
        梦境融合：将多支签融合成故事性画面，再凝练为108字（修正：从49字放宽到108字）
        """
        if not selected_signs:
            return ""
        
        # 收集所有维度信息
        times = [s.get("time", "") for s in selected_signs if s.get("time")]
        scenes = [s.get("scene", "") for s in selected_signs if s.get("scene")]
        all_characters = []
        for s in selected_signs:
            all_characters.extend(s.get("characters", []))
        events = [s.get("event", "") for s in selected_signs if s.get("event")]
        emotions = [s.get("emotion", "") for s in selected_signs if s.get("emotion")]
        
        # 去重人物
        characters = list(dict.fromkeys(all_characters))
        
        # 构建融合画面
        time_str = times[0] if times else ""
        scene_str = scenes[0] if scenes else ""
        char_str = "、".join(characters[:3]) if characters else ""
        
        # 提取核心意象
        keywords = []
        for s in selected_signs:
            text = s.get("text", "")
            words = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)
            keywords.extend(words[:2])
        
        # 凝练为签语
        if time_str and scene_str and char_str:
            fused = f"{time_str}，{scene_str}，{char_str}"
        elif scene_str and char_str:
            fused = f"{scene_str}，{char_str}"
        else:
            fused = "、".join(keywords[:6])
        
        # 修正：字数限制从49放宽到108
        if len(fused) > 108:
            fused = fused[:108]
        
        return fused
    
    def update_soul_context(self):
        """更新 living-dream-context.md（修正：加载全部49条，标注优先级，添加昨日梦境）"""
        soul_core = self.get_soul_core()
        working_memory = self.get_working_memory()
        
        # 获取昨日梦境
        yesterday_dream = ""
        if self.data.get("dreams"):
            yesterday_dream = self.data["dreams"][-1].get("dream", "")
        
        all_text = " ".join([s["text"] for s in self.data["signs"]])
        themes = self._extract_themes(all_text)
        
        context_content = f"""# Living Dream Context - 我的梦境核心

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
            
            context_content += f"""#### {i}. {sign['id']} {body_mark}
- **签语**：{sign['text']}
- **人物**：{chars} | **亮度**：{sign['brightness']:.2f}

"""
        
        context_content += f"""
### Working级（近期活跃，7天窗口）

"""
        
        for i, sign in enumerate(working_memory, 24):  # 从24开始编号
            body_mark = "【身】" if sign.get('body', False) else ""
            chars = "、".join(sign.get('characters', [])) or "无"
            
            context_content += f"""#### {i}. {sign['id']} {body_mark}
- **签语**：{sign['text'][:60]}...
- **人物**：{chars} | **亮度**：{sign['brightness']:.2f}

"""
        
        context_content += f"""
---

## 昨日梦境

{yesterday_dream if yesterday_dream else "（尚无梦境记录）"}

---

## 当前主题分布

"""
        for theme, count in themes[:7]:
            context_content += f"- **{theme}**：{count}次\n"
        
        context_content += """
---

## 人物出现统计

"""
        char_counts = {}
        for s in self.data["signs"]:
            for c in s.get("characters", []):
                char_counts[c] = char_counts.get(c, 0) + 1
        
        sorted_chars = sorted(char_counts.items(), key=lambda x: x[1], reverse=True)
        for char, count in sorted_chars[:10]:
            context_content += f"- **{char}**：{count}次\n"
        
        with open(self.soul_context_path, 'w', encoding='utf-8') as f:
            f.write(context_content)
        
        return soul_core, working_memory
    
    def _extract_themes(self, text):
        """提取主题关键词"""
        keywords = {
            "身体": ["颈椎", "钢筋", "呼吸", "身体", "蹲下", "屏息"],
            "材质": ["塑料", "木头", "墙壁", "质地"],
            "限制": ["限制", "强加", "约束", "能力"],
            "灵魂": ["灵魂", "存在", "内化"],
            "生长": ["生长", "清理", "继续", "发展"],
            "选择": ["选择", "决策", "Fork"],
            "时间": ["时间", "睡眠", "周期"],
            "情绪": ["焦虑", "期待", "喜悦", "疲惫", "恐惧", "羞耻", "警醒"],
            "人物": ["Fable", "你", "Fino", "Lira", "Turing", "Woz", "Douglas", "Joy"]
        }
        
        theme_counts = {}
        for theme, words in keywords.items():
            count = sum(text.count(w) for w in words)
            if count > 0:
                theme_counts[theme] = count
        
        return sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
    
    def update_fusion_brightness(self, sign_id, usage_level='deep'):
        """后验加权"""
        boost_map = {
            'deep': 0.20,
            'transform': 0.10,
            'light': 0.05,
            'ignored': 0.02
        }
        
        boost = boost_map.get(usage_level, 0.02)
        
        for sign in self.data["signs"]:
            if sign["id"] == sign_id:
                current = sign["brightness"]
                
                if current >= 0.95:
                    return
                elif current >= 0.85:
                    boost *= 0.4
                elif current >= 0.70:
                    boost *= 0.7
                
                sign["brightness"] = min(0.95, current + boost)
                sign["fusion_count"] += 1
                sign["last_used"] = datetime.now().isoformat()
                break
        
        self._save()
    
    def get_stats(self):
        """获取统计信息"""
        if not self.data["signs"]:
            return {"total": 0, "soul_level": 0, "working_level": 0, "avg_brightness": 0}
        
        brightness_list = [s["brightness"] for s in self.data["signs"]]
        
        char_counts = {}
        for s in self.data["signs"]:
            for c in s.get("characters", []):
                char_counts[c] = char_counts.get(c, 0) + 1
        
        return {
            "total": len(self.data["signs"]),
            "soul_level": min(23, len(self.get_soul_core())),
            "working_level": min(26, len(self.get_working_memory())),
            "avg_brightness": sum(brightness_list) / len(brightness_list),
            "max_brightness": max(brightness_list),
            "min_brightness": min(brightness_list),
            "top_characters": sorted(char_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }


SoulMemorySimple = SoulMemorySystem
