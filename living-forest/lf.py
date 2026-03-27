#!/usr/bin/env python3
"""
Living Forest CLI 入口点
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lf.cli import main

if __name__ == "__main__":
    main()
