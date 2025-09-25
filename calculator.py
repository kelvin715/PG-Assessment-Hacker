#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

expression_map = {
    "□+□+□": lambda a, b, c, d=None: a + b + c,
    "□−□+□": lambda a, b, c, d=None: a - b + c,
    "□×□+□": lambda a, b, c, d=None: a * b + c,
    "□×□−□": lambda a, b, c, d=None: a * b - c,
    "□×□×□": lambda a, b, c, d=None: a * b * c,
    "□+□+□+□": lambda a, b, c, d: a + b + c + d,
    "□+□+□−□": lambda a, b, c, d: a + b + c - d,
    "□×□+□+□": lambda a, b, c, d: a * b + c + d,
    "□×□+□−□": lambda a, b, c, d: a * b + c - d,
    "□×□×□+□": lambda a, b, c, d: a * b * c + d,
    "□×□×□−□": lambda a, b, c, d: a * b * c - d,
}


def generate_expressions():
    expr_db = []
    for a in range(1, 10):
        for b in range(1, 10):
            for c in range(1, 10):
                for d in range(1, 10):
                    for key, func in expression_map.items():
                        num_placeholders = key.count("□")
                        nums = [a, b, c, d][:num_placeholders]
                        if len(set(nums)) < num_placeholders:
                            continue
                        try:
                            result = func(a, b, c, d)
                            expr = key.replace("□", "{}").format(*nums)
                            expr_db.append((key, result, expr))
                        except Exception:
                            continue
    return expr_db


def find_expression(expr_db, pattern: str, target: int):
    for pat, val, expr in expr_db:
        if pat == pattern and val == target:
            return expr.replace("*", "×").replace("-", "−")
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pattern",
        required=False,
        choices=list(expression_map.keys()),
        help="选择计算模式",
    )
    parser.add_argument(
        "--target",
        required=False,
        type=int,
        help="目标值（整数）",
    )
    args = parser.parse_args()

    # If not provided, enter interactive mode
    if args.pattern is None or args.target is None:
        patterns = list(expression_map.keys())
        print("请选择计算模式（输入编号）:")
        for idx, pat in enumerate(patterns, start=1):
            print(f"  {idx}. {pat}")
        # Select mode
        while True:
            sel = input("编号: ").strip()
            if not sel.isdigit():
                print("请输入有效编号")
                continue
            sel_idx = int(sel)
            if 1 <= sel_idx <= len(patterns):
                args.pattern = patterns[sel_idx - 1]
                break
            print("编号超出范围")
        # Input target
        while True:
            t = input("请输入目标整数 target: ").strip()
            try:
                args.target = int(t)
                break
            except Exception:
                print("请输入有效整数")

    database = generate_expressions()
    matched = find_expression(database, args.pattern, args.target)
    if matched is None:
        print("未找到匹配")
    else:
        print(matched)


if __name__ == "__main__":
    while True:
        try:    
            main()
        except Exception as e:
            print(f"发生错误: {e}")
            print   ("请重新开始")
            continue
        break


