#!/usr/bin/env python3
"""
数据迁移脚本：将 _tree.md 转换为 _tree.json
"""

import re
import json
from pathlib import Path
from datetime import datetime


def parse_tree_md(content: str) -> dict:
    """解析 Markdown 树结构"""
    data = {
        "meta": {},
        "nodes": [],
        "evolution": [],
        "resurrections": []
    }
    
    lines = content.split('\n')
    current_section = None
    in_code_block = False
    code_content = []
    
    # 提取标题
    if lines and lines[0].startswith('# '):
        data["meta"]["name"] = lines[0][2:].strip()
    
    # 提取元信息
    for line in lines[1:20]:  # 前20行
        if line.startswith('> 生成时间：'):
            time_str = line.replace('> 生成时间：', '').strip()
            try:
                dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
                data["meta"]["created_at"] = dt.isoformat()
            except:
                pass
        elif line.startswith('> 版本：'):
            data["meta"]["version"] = line.replace('> 版本：', '').strip()
        elif line.startswith('> 状态：'):
            status_text = line.replace('> 状态：', '').strip()
            if '🪦' in status_text or '归档' in status_text:
                data["meta"]["status"] = "archived"
            else:
                data["meta"]["status"] = "active"
    
    # 提取项目描述
    for i, line in enumerate(lines):
        if line == '## 项目根':
            # 收集描述直到下一个标题
            desc_lines = []
            for j in range(i+1, len(lines)):
                if lines[j].startswith('##'):
                    break
                desc_lines.append(lines[j])
            data["meta"]["description"] = '\n'.join(desc_lines).strip()
            break
    
    # 提取树结构（主干、分支、墓地）
    for i, line in enumerate(lines):
        if line.startswith('```tree'):
            in_code_block = True
            code_content = []
            continue
        elif line.startswith('```') and in_code_block:
            in_code_block = False
            nodes = parse_tree_lines(code_content)
            # 根据当前章节确定类型
            section_type = "trunk"
            for j in range(max(0, i-20), i):
                if '主干' in lines[j] or 'Trunk' in lines[j]:
                    section_type = "trunk"
                elif '分支' in lines[j] or 'Branches' in lines[j]:
                    section_type = "branch"
            for node in nodes:
                node["type"] = section_type
            data["nodes"].extend(nodes)
            continue
        
        if in_code_block:
            code_content.append(line)
    
    # 提取墓地表格
    for i, line in enumerate(lines):
        if '| 编号 |' in line or '|编号|' in line:
            # 读取表格
            table_lines = []
            for j in range(i, len(lines)):
                if lines[j].strip() == '':
                    break
                table_lines.append(lines[j])
            
            # 跳过表头和分隔行
            for table_line in table_lines[2:]:
                parts = [p.strip() for p in table_line.split('|')]
                parts = [p for p in parts if p]  # 移除空项
                if len(parts) >= 3:
                    node = {
                        "id": parts[0],
                        "label": parts[1],
                        "status": "archived",
                        "type": "graveyard",
                        "description": parts[3] if len(parts) > 3 else ""
                    }
                    data["nodes"].append(node)
    
    # 提取演化历史
    in_evolution = False
    for line in lines:
        if '## 演化历史' in line:
            in_evolution = True
            continue
        elif line.startswith('## ') and in_evolution:
            break
        
        if in_evolution and line.strip().startswith('- **'):
            # 解析版本条目
            match = re.search(r'- \*\*(v?\d+)\*\*\s*\(([^)]+)\)', line)
            if match:
                version, date_str = match.groups()
                data["evolution"].append({
                    "version": version,
                    "date": date_str,
                    "summary": "",
                    "changes": []
                })
    
    # 确保默认值
    data["meta"].setdefault("version", "v1")
    data["meta"].setdefault("status", "active")
    data["meta"].setdefault("created_at", datetime.now().isoformat())
    data["meta"].setdefault("updated_at", datetime.now().isoformat())
    
    return data


def parse_tree_lines(lines: list) -> list:
    """解析树形文本，返回节点列表"""
    nodes = []
    node_stack = []  # 用于跟踪层级关系
    
    for line in lines:
        if not line.strip():
            continue
        
        # 匹配树形结构
        # ├── 001 立项 [✅ 完成]
        # └── 002 抽签机 [🔄 进行中]
        # │   ├── 002.1 签数生成 [✅]
        match = re.match(r'^([├└│ ]*)[├└]──\s+(\S+)\s+(.+?)\s*\[(.+?)\]', line)
        if match:
            prefix, node_id, label, status_text = match.groups()
            
            # 计算层级
            level = prefix.count('│') + prefix.count(' ') // 4 + 1
            
            # 解析状态
            status_map = {
                '✅': 'done',
                '🔄': 'active',
                '⏸️': 'draft',
                '🧪': 'research',
                '🪦': 'archived',
                '📝': 'draft',
                '⚠️': 'blocked'
            }
            
            status = 'draft'
            for icon, st in status_map.items():
                if icon in status_text:
                    status = st
                    break
            
            # 确定父节点
            parent = None
            while node_stack and node_stack[-1]["level"] >= level:
                node_stack.pop()
            if node_stack:
                parent = node_stack[-1]["id"]
            
            node = {
                "id": node_id,
                "label": label.strip(),
                "status": status,
                "type": "trunk",  # 默认，会被覆盖
                "parent": parent,
                "children": [],
                "description": ""
            }
            nodes.append(node)
            node_stack.append({"id": node_id, "level": level})
            
            # 更新父节点的 children
            if parent:
                for n in nodes:
                    if n["id"] == parent:
                        if node_id not in n["children"]:
                            n["children"].append(node_id)
                        break
    
    return nodes


def migrate_project(project_dir: Path) -> Path:
    """迁移单个项目"""
    tree_md = project_dir / "_tree.md"
    tree_json = project_dir / "_tree.json"
    
    if not tree_md.exists():
        print(f"跳过: {tree_md} 不存在")
        return None
    
    print(f"迁移: {tree_md} -> {tree_json}")
    
    content = tree_md.read_text(encoding='utf-8')
    data = parse_tree_md(content)
    
    with open(tree_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ {len(data['nodes'])} 个节点")
    return tree_json


def main():
    """主函数"""
    base_dir = Path(__file__).parent / "examples"
    
    projects = ["soul-memory", "token-saver"]
    
    for proj in projects:
        project_dir = base_dir / proj
        if project_dir.exists():
            migrate_project(project_dir)
        else:
            print(f"项目不存在: {project_dir}")
    
    print("\n迁移完成！")


if __name__ == "__main__":
    main()
