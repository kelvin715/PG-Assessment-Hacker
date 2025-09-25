#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools
from typing import List, Tuple, Optional

class VisualReasoningSolver:
    def __init__(self):
        self.shapes = {
            '1': '●',  # 圆形
            '2': '▲',  # 三角形
            '3': '■',  # 正方形
            '4': '✚'   # 十字形
        }
        
        # 题型定义
        self.question_types = {
            '1': '单次变换',
            '2': '两次变换(第1次固定)', 
            '3': '两次变换(第2次固定)',
            '4': '三次变换(第1次不固定,第2,3次固定)',
            '5': '三次变换(第2次不固定,第1,3次固定)',
            '6': '三次变换(第3次不固定,第1,2次固定)',
            '7': '双管道'
        }
        
        self.all_permutations = self._generate_all_permutations()
        
    def _generate_all_permutations(self) -> List[str]:
        """生成所有可能的4位排列变换"""
        perms = []
        for perm in itertools.permutations('1234'):
            perms.append(''.join(perm))
        return perms

    def display_menu(self):
        """显示主菜单"""
        print("\n" + "="*50)
        print("管道推理题求解器")
        print("="*50)
        print("支持的题型:")
        for key, value in self.question_types.items():
            auto_indicator = " 🤖" if key in ['1', '2', '3', '4', '5', '6'] else ""
            print(f"  {key}. {value}{auto_indicator}")
        print("\n支持的形状:")
        for key, value in self.shapes.items():
            print(f"  {key}: {value}")
        print("\n题型1只需要输入输出序列，题型2-6需要输入固定变换，双管道需要输入两次变换选项！")

    def get_question_type(self) -> str:
        """获取题型选择"""
        while True:
            print("\n请选择题型 (1-7):")
            choice = input("输入编号: ").strip()
            if choice in self.question_types:
                print(f"已选择: {self.question_types[choice]}")
                return choice
            print("无效选择，请重新输入!")

    def get_mode_choice(self, question_type: str) -> str:
        """获取模式选择（手动或自动）"""
        if question_type == '1':
            # Q1题型完全自动推导
            print("💡 使用自动模式: 将根据输入输出序列自动推导变换选项")
            return 'auto'
        elif question_type in ['2', '3', '4', '5', '6']:
            # Q2-Q6题型半自动模式：需要输入固定变换，自动推导可选变换
            print("💡 使用半自动模式: 请输入已知的固定变换，程序将自动推导可选变换")
            return 'semi_auto'
        else:
            # Q7题型使用手动模式
            return 'manual'

    def parse_sequence(self, sequence_str: str) -> List[List[str]]:
        """解析序列字符串，返回形状序列"""
        # 支持多种输入格式
        # 格式1: "1234" -> [['●', '▲', '■', '✚']]
        # 格式2: "1234,2341,3412" -> [['●', '▲', '■', '✚'], ['▲', '■', '✚', '●'], ...]
        
        sequences = []
        if ',' in sequence_str:
            # 多个序列
            for seq in sequence_str.split(','):
                seq = seq.strip()
                if seq:
                    shapes = [self.shapes.get(char, char) for char in seq if char in self.shapes]
                    if shapes:
                        sequences.append(shapes)
        else:
            # 单个序列
            shapes = [self.shapes.get(char, char) for char in sequence_str if char in self.shapes]
            if shapes:
                sequences.append(shapes)
        
        return sequences

    def get_input_output_sequences(self) -> Tuple[List[List[str]], List[List[str]]]:
        """获取输入和输出序列"""
        print("\n请输入序列 (使用数字1-4代表形状: ●▲■✚)")
        print("多个序列用逗号分隔，例如: 1234,2341,3412")
        
        while True:
            input_str = input("\n输入序列: ").strip()
            if input_str:
                input_sequences = self.parse_sequence(input_str)
                if input_sequences:
                    print("输入序列:", input_sequences)
                    break
            print("无效输入，请重新输入!")
        
        while True:
            output_str = input("输出序列: ").strip()
            if output_str:
                output_sequences = self.parse_sequence(output_str)
                if output_sequences:
                    print("输出序列:", output_sequences)
                    break
            print("无效输入，请重新输入!")
        
        return input_sequences, output_sequences

    def auto_solve_q1(self, input_seqs: List[List[str]], output_seqs: List[List[str]]) -> Optional[List[str]]:
        """自动为Q1题型生成可能的变换选项"""
        if not input_seqs or not output_seqs:
            return None
            
        input_seq = input_seqs[0]
        target_seq = output_seqs[0]
        
        # 找到所有可能的变换
        possible_transforms = []
        for perm in self.all_permutations:
            result = self.apply_permutation(input_seq, perm)
            if result == target_seq:
                possible_transforms.append(perm)
        
        if possible_transforms:
            # 如果找到多个可能的变换，从中选择3个作为选项
            # 确保正确答案在其中，其他的作为干扰项
            if len(possible_transforms) >= 3:
                return possible_transforms[:3]
            else:
                # 不够3个，添加一些其他变换作为干扰项
                options = possible_transforms[:]
                for perm in self.all_permutations:
                    if perm not in options:
                        options.append(perm)
                        if len(options) >= 3:
                            break
                return options[:3]
        
        return None

    def auto_solve_q2_q3(self, input_seqs: List[List[str]], output_seqs: List[List[str]], 
                         question_type: str) -> Optional[Tuple[str, List[str]]]:
        """自动为Q2-Q3题型生成固定变换和可选变换"""
        if not input_seqs or not output_seqs:
            return None
            
        input_seq = input_seqs[0]
        target_seq = output_seqs[0]
        
        # 尝试所有可能的两次变换组合，排除恒等变换
        valid_combinations = []
        
        for perm1 in self.all_permutations:
            # 排除恒等变换，确保是有意义的变换
            if perm1 == '1234':
                continue
                
            for perm2 in self.all_permutations:
                if question_type == '2':  # 第一次固定，第二次选择
                    intermediate = self.apply_permutation(input_seq, perm1)
                    result = self.apply_permutation(intermediate, perm2)
                    if result == target_seq:
                        valid_combinations.append((perm1, perm2))  # (固定的, 可选的)
                else:  # question_type == '3', 第一次选择，第二次固定
                    # 排除第二次变换为恒等变换的情况
                    if perm2 == '1234':
                        continue
                    intermediate = self.apply_permutation(input_seq, perm1)
                    result = self.apply_permutation(intermediate, perm2)
                    if result == target_seq:
                        valid_combinations.append((perm2, perm1))  # (固定的, 可选的)
        
        if valid_combinations:
            # 选择第一个有效组合作为基础
            fixed_perm, correct_option = valid_combinations[0]
            
            # 生成3个选项，包含正确答案，排除恒等变换
            options = [correct_option]
            for perm in self.all_permutations:
                if perm not in options and perm != '1234':
                    options.append(perm)
                    if len(options) >= 3:
                        break
            
            return fixed_perm, options[:3]
        
        return None

    def auto_solve_q4_q6(self, input_seqs: List[List[str]], output_seqs: List[List[str]], 
                         question_type: str) -> Optional[Tuple[str, str, List[str], int]]:
        """自动为Q4-Q6题型生成两个固定变换和一个可选变换"""
        if not input_seqs or not output_seqs:
            return None
            
        input_seq = input_seqs[0]
        target_seq = output_seqs[0]
        variable_position = int(question_type) - 3  # Q4->1, Q5->2, Q6->3
        
        # 尝试所有可能的三次变换组合，排除恒等变换
        valid_combinations = []
        
        for perm1 in self.all_permutations:
            # 排除恒等变换
            if perm1 == '1234':
                continue
            for perm2 in self.all_permutations:
                if perm2 == '1234':
                    continue
                for perm3 in self.all_permutations:
                    if perm3 == '1234':
                        continue
                        
                    intermediate1 = self.apply_permutation(input_seq, perm1)
                    intermediate2 = self.apply_permutation(intermediate1, perm2)
                    result = self.apply_permutation(intermediate2, perm3)
                    
                    if result == target_seq:
                        if variable_position == 1:  # Q4: 第1次可选
                            valid_combinations.append((perm1, perm2, perm3))
                        elif variable_position == 2:  # Q5: 第2次可选
                            valid_combinations.append((perm2, perm1, perm3))
                        else:  # variable_position == 3, Q6: 第3次可选
                            valid_combinations.append((perm3, perm1, perm2))
        
        if valid_combinations:
            # 选择第一个有效组合
            correct_option, fixed1, fixed2 = valid_combinations[0]
            
            # 生成3个选项，包含正确答案，排除恒等变换
            options = [correct_option]
            for perm in self.all_permutations:
                if perm not in options and perm != '1234':
                    options.append(perm)
                    if len(options) >= 3:
                        break
            
            return fixed1, fixed2, options[:3], variable_position
        
        return None

    def semi_auto_solve_q2_q3(self, input_seqs: List[List[str]], output_seqs: List[List[str]], 
                              question_type: str, fixed_perm: str) -> Optional[List[str]]:
        """半自动为Q2-Q3题型：给定固定变换，推导可选变换选项"""
        if not input_seqs or not output_seqs:
            return None
            
        input_seq = input_seqs[0]
        target_seq = output_seqs[0]
        
        # 根据题型确定变换顺序
        if question_type == '2':  # 第一次固定，第二次选择
            intermediate = self.apply_permutation(input_seq, fixed_perm)
            print(f"第一次变换后: {input_seq} -> {intermediate}")
            
            # 找到能从中间结果到目标的变换
            correct_option = None
            for perm in self.all_permutations:
                result = self.apply_permutation(intermediate, perm)
                if result == target_seq:
                    correct_option = perm
                    break
        
        else:  # question_type == '3', 第一次选择，第二次固定
            # 需要找到第一次变换，使得经过固定的第二次变换后得到目标
            correct_option = None
            for perm in self.all_permutations:
                intermediate = self.apply_permutation(input_seq, perm)
                result = self.apply_permutation(intermediate, fixed_perm)
                if result == target_seq:
                    correct_option = perm
                    break
        
        if correct_option:
            # 生成3个选项，包含正确答案
            options = [correct_option]
            for perm in self.all_permutations:
                if perm not in options:
                    options.append(perm)
                    if len(options) >= 3:
                        break
            
            return options[:3]
        
        return None

    def semi_auto_solve_q4_q6(self, input_seqs: List[List[str]], output_seqs: List[List[str]], 
                              question_type: str, fixed1: str, fixed2: str) -> Optional[List[str]]:
        """半自动为Q4-Q6题型：给定两个固定变换，推导可选变换选项"""
        if not input_seqs or not output_seqs:
            return None
            
        input_seq = input_seqs[0]
        target_seq = output_seqs[0]
        variable_position = int(question_type) - 3  # Q4->1, Q5->2, Q6->3
        
        correct_option = None
        
        if variable_position == 1:  # Q4: 第1次可选，第2,3次固定
            for perm in self.all_permutations:
                intermediate1 = self.apply_permutation(input_seq, perm)
                intermediate2 = self.apply_permutation(intermediate1, fixed1)
                result = self.apply_permutation(intermediate2, fixed2)
                if result == target_seq:
                    correct_option = perm
                    break
                    
        elif variable_position == 2:  # Q5: 第2次可选，第1,3次固定
            intermediate1 = self.apply_permutation(input_seq, fixed1)
            for perm in self.all_permutations:
                intermediate2 = self.apply_permutation(intermediate1, perm)
                result = self.apply_permutation(intermediate2, fixed2)
                if result == target_seq:
                    correct_option = perm
                    break
                    
        else:  # Q6: 第3次可选，第1,2次固定
            intermediate1 = self.apply_permutation(input_seq, fixed1)
            intermediate2 = self.apply_permutation(intermediate1, fixed2)
            for perm in self.all_permutations:
                result = self.apply_permutation(intermediate2, perm)
                if result == target_seq:
                    correct_option = perm
                    break
        
        if correct_option:
            # 生成3个选项，包含正确答案
            options = [correct_option]
            for perm in self.all_permutations:
                if perm not in options:
                    options.append(perm)
                    if len(options) >= 3:
                        break
            
            return options[:3]
        
        return None

    def get_fixed_permutation(self, prompt: str) -> str:
        """获取固定变换输入"""
        print(f"\n{prompt}")
        print("排列规则说明: 2314表示把原位置2,3,1,4的元素分别放到新位置1,2,3,4")
        
        while True:
            perm_str = input("请输入固定变换: ").strip()
            if len(perm_str) == 4 and all(c in '1234' for c in perm_str):
                print(f"固定变换: {perm_str}")
                return perm_str
            print("请输入4位排列数字!")

    def get_q1_options(self) -> List[str]:
        """Q1: 获取3个变换选项"""
        print("\n=== Q1 单次变换 ===")
        print("排列规则说明: 2314表示把原位置2,3,1,4的元素分别放到新位置1,2,3,4")
        
        while True:
            options_str = input("请输入3个排列选项 (空格分隔，如: 2314 2341 3241): ").strip()
            options = options_str.split()
            if len(options) == 3 and all(len(opt) == 4 and all(c in '1234' for c in opt) for opt in options):
                print(f"变换选项: {options}")
                return options
            print("请输入3个4位排列数字，用空格分隔!")

    def get_q2_q3_options(self, question_type: str) -> Tuple[str, List[str]]:
        """Q2-Q3: 获取两次变换，一次固定，一次有3种可能"""
        if question_type == '2':
            print("\n=== Q2 两次变换(选后面-第一次固定) ===")
            print("排列规则说明: 2314表示把原位置2,3,1,4的元素分别放到新位置1,2,3,4")
            
            # 第一次变换固定
            while True:
                fixed_str = input("请输入第一次变换(固定): ").strip()
                if len(fixed_str) == 4 and all(c in '1234' for c in fixed_str):
                    print(f"第一次变换(固定): {fixed_str}")
                    break
                print("请输入4位排列数字!")
            
            # 第二次变换有3种可能
            while True:
                options_str = input("请输入第二次变换的3个选项 (空格分隔): ").strip()
                options = options_str.split()
                if len(options) == 3 and all(len(opt) == 4 and all(c in '1234' for c in opt) for opt in options):
                    print(f"第二次变换选项: {options}")
                    return fixed_str, options
                print("请输入3个4位排列数字，用空格分隔!")
        
        else:  # question_type == '3'
            print("\n=== Q3 两次变换(选首次-第二次固定) ===")
            print("排列规则说明: 2314表示把原位置2,3,1,4的元素分别放到新位置1,2,3,4")
            
            # 第一次变换有3种可能
            while True:
                options_str = input("请输入第一次变换的3个选项 (空格分隔): ").strip()
                options = options_str.split()
                if len(options) == 3 and all(len(opt) == 4 and all(c in '1234' for c in opt) for opt in options):
                    print(f"第一次变换选项: {options}")
                    break
                print("请输入3个4位排列数字，用空格分隔!")
            
            # 第二次变换固定
            while True:
                fixed_str = input("请输入第二次变换(固定): ").strip()
                if len(fixed_str) == 4 and all(c in '1234' for c in fixed_str):
                    print(f"第二次变换(固定): {fixed_str}")
                    return fixed_str, options
                print("请输入4位排列数字!")

    def get_q4_q6_options(self, question_type: str) -> Tuple[str, str, List[str], int]:
        """Q4-Q6: 获取三次变换，两次固定，一次有3种可能"""
        
        if question_type == '4':
            print("\n=== Q4 三次变换(第1次不固定,第2,3次固定) ===")
            variable_position = 1
        elif question_type == '5':
            print("\n=== Q5 三次变换(第2次不固定,第1,3次固定) ===")
            variable_position = 2
        else:  # question_type == '6'
            print("\n=== Q6 三次变换(第3次不固定,第1,2次固定) ===")
            variable_position = 3
            
        print("排列规则说明: 2314表示把原位置2,3,1,4的元素分别放到新位置1,2,3,4")
        
        if variable_position == 1:
            # 第一次变换有3种可能
            while True:
                options_str = input("请输入第一次变换的3个选项 (空格分隔): ").strip()
                options = options_str.split()
                if len(options) == 3 and all(len(opt) == 4 and all(c in '1234' for c in opt) for opt in options):
                    print(f"第一次变换选项: {options}")
                    break
                print("请输入3个4位排列数字，用空格分隔!")
            
            # 第二次变换固定
            while True:
                fixed1_str = input("请输入第二次变换(固定): ").strip()
                if len(fixed1_str) == 4 and all(c in '1234' for c in fixed1_str):
                    print(f"第二次变换(固定): {fixed1_str}")
                    break
                print("请输入4位排列数字!")
            
            # 第三次变换固定
            while True:
                fixed2_str = input("请输入第三次变换(固定): ").strip()
                if len(fixed2_str) == 4 and all(c in '1234' for c in fixed2_str):
                    print(f"第三次变换(固定): {fixed2_str}")
                    return fixed1_str, fixed2_str, options, variable_position
                print("请输入4位排列数字!")
                
        elif variable_position == 2:
            # 第一次变换固定
            while True:
                fixed1_str = input("请输入第一次变换(固定): ").strip()
                if len(fixed1_str) == 4 and all(c in '1234' for c in fixed1_str):
                    print(f"第一次变换(固定): {fixed1_str}")
                    break
                print("请输入4位排列数字!")
            
            # 第二次变换有3种可能
            while True:
                options_str = input("请输入第二次变换的3个选项 (空格分隔): ").strip()
                options = options_str.split()
                if len(options) == 3 and all(len(opt) == 4 and all(c in '1234' for c in opt) for opt in options):
                    print(f"第二次变换选项: {options}")
                    break
                print("请输入3个4位排列数字，用空格分隔!")
            
            # 第三次变换固定
            while True:
                fixed2_str = input("请输入第三次变换(固定): ").strip()
                if len(fixed2_str) == 4 and all(c in '1234' for c in fixed2_str):
                    print(f"第三次变换(固定): {fixed2_str}")
                    return fixed1_str, fixed2_str, options, variable_position
                print("请输入4位排列数字!")
                
        else:  # variable_position == 3
            # 第一次变换固定
            while True:
                fixed1_str = input("请输入第一次变换(固定): ").strip()
                if len(fixed1_str) == 4 and all(c in '1234' for c in fixed1_str):
                    print(f"第一次变换(固定): {fixed1_str}")
                    break
                print("请输入4位排列数字!")
            
            # 第二次变换固定
            while True:
                fixed2_str = input("请输入第二次变换(固定): ").strip()
                if len(fixed2_str) == 4 and all(c in '1234' for c in fixed2_str):
                    print(f"第二次变换(固定): {fixed2_str}")
                    break
                print("请输入4位排列数字!")
            
            # 第三次变换有3种可能
            while True:
                options_str = input("请输入第三次变换的3个选项 (空格分隔): ").strip()
                options = options_str.split()
                if len(options) == 3 and all(len(opt) == 4 and all(c in '1234' for c in opt) for opt in options):
                    print(f"第三次变换选项: {options}")
                    return fixed1_str, fixed2_str, options, variable_position
                print("请输入3个4位排列数字，用空格分隔!")

    def get_permutation_options(self) -> Tuple[List[str], List[str]]:
        """获取Q11两步排列变换的选项"""
        
        print("\n=== 第一步排列选项 ===")
        while True:
            options_str = input("请输入第一步的3个排列选项 (空格分隔，如: 2314 2341 3241): ").strip()
            options = options_str.split()
            if len(options) == 3 and all(len(opt) == 4 and all(c in '1234' for c in opt) for opt in options):
                print(f"第一步选项: {options}")
                first_options = options
                break
            print("请输入3个4位排列数字，用空格分隔!")
        
        print("\n=== 第二步排列选项 ===")
        while True:
            options_str = input("请输入第二步的3个排列选项 (空格分隔，如: 2314 2341 3241): ").strip()
            options = options_str.split()
            if len(options) == 3 and all(len(opt) == 4 and all(c in '1234' for c in opt) for opt in options):
                print(f"第二步选项: {options}")
                second_options = options
                break
            print("请输入3个4位排列数字，用空格分隔!")
        
        return first_options, second_options


    def apply_permutation(self, sequence: List[str], permutation: str) -> List[str]:
        """
        应用排列变换
        permutation: 如 "2314" 表示新位置i的元素来自原位置permutation[i-1]
        """
        if len(permutation) != len(sequence):
            return sequence
        
        result = [''] * len(sequence)
        for new_pos in range(len(sequence)):
            # permutation[new_pos] 告诉我们新位置new_pos的元素来自哪个原位置
            old_pos = int(permutation[new_pos]) - 1  # 转换为0索引
            result[new_pos] = sequence[old_pos]
        
        return result

    def solve_two_step_permutation(self, input_seqs: List[List[str]], 
                                  output_seqs: List[List[str]], 
                                  first_options: List[str], 
                                  second_options: List[str]) -> Tuple[int, int]:
        """
        Q11专用：解决两步排列问题
        """
        if not input_seqs or not output_seqs:
            return -1, -1
            
        input_seq = input_seqs[0]
        target_seq = output_seqs[0]
        
        # 尝试所有组合
        for i, perm1 in enumerate(first_options):
            # 应用第一次排列
            intermediate = self.apply_permutation(input_seq, perm1)
            
            for j, perm2 in enumerate(second_options):
                # 应用第二次排列
                final_result = self.apply_permutation(intermediate, perm2)
                
                # 检查是否匹配目标
                if final_result == target_seq:
                    print(f"\n✅ 找到正确的排列组合!")
                    print(f"第一步: 选择排列{i+1} ({perm1})")
                    print(f"  {input_seq} -> {intermediate}")
                    print(f"第二步: 选择排列{j+1} ({perm2})")
                    print(f"  {intermediate} -> {final_result}")
                    print(f"结果匹配目标: {final_result} = {target_seq}")
                    
                    return i+1, j+1
        
        print("\n❌ 未找到匹配的排列组合")
        return -1, -1

    def solve_q1(self, input_seqs: List[List[str]], output_seqs: List[List[str]], 
                 permutation_options: List[str]) -> int:
        """Q1: 单次变换"""
        if not input_seqs or not output_seqs:
            return -1
            
        input_seq = input_seqs[0]
        target_seq = output_seqs[0]
        
        print(f"\n分析Q1单次变换:")
        print(f"输入: {input_seq}")
        print(f"目标: {target_seq}")
        
        for i, perm in enumerate(permutation_options):
            result = self.apply_permutation(input_seq, perm)
            if result == target_seq:
                print(f"\n✅ 找到正确的变换!")
                print(f"选择变换 {i+1} ({perm})")
                print(f"  {input_seq} -> {result}")
                return i + 1
        
        print("\n❌ 未找到匹配的变换")
        return -1

    def solve_q2_q3(self, input_seqs: List[List[str]], output_seqs: List[List[str]], 
                    fixed_perm: str, variable_options: List[str], question_type: str) -> int:
        """Q2-Q3: 两次变换，一次固定，一次可选"""
        if not input_seqs or not output_seqs:
            return -1
            
        input_seq = input_seqs[0]
        target_seq = output_seqs[0]
        
        print(f"\n分析Q{question_type}两次变换:")
        print(f"输入: {input_seq}")
        print(f"目标: {target_seq}")
        
        if question_type == '2':  # 选后面，第一次固定
            print(f"第一次变换(固定): {fixed_perm}")
            intermediate = self.apply_permutation(input_seq, fixed_perm)
            print(f"中间结果: {input_seq} -> {intermediate}")
            
            for i, perm in enumerate(variable_options):
                result = self.apply_permutation(intermediate, perm)
                if result == target_seq:
                    print(f"\n✅ 找到正确的第二次变换!")
                    print(f"第二次变换选择 {i+1} ({perm})")
                    print(f"  {intermediate} -> {result}")
                    return i + 1
        
        else:  # question_type == '3', 选首次，第二次固定
            print(f"第二次变换(固定): {fixed_perm}")
            
            for i, perm in enumerate(variable_options):
                intermediate = self.apply_permutation(input_seq, perm)
                result = self.apply_permutation(intermediate, fixed_perm)
                if result == target_seq:
                    print(f"\n✅ 找到正确的第一次变换!")
                    print(f"第一次变换选择 {i+1} ({perm})")
                    print(f"  {input_seq} -> {intermediate} -> {result}")
                    return i + 1
        
        print("\n❌ 未找到匹配的变换")
        return -1

    def solve_q4_q6(self, input_seqs: List[List[str]], output_seqs: List[List[str]], 
                    fixed1: str, fixed2: str, variable_options: List[str], variable_position: int) -> int:
        """Q4-Q6: 三次变换，两次固定，一次可选"""
        if not input_seqs or not output_seqs:
            return -1
            
        input_seq = input_seqs[0]
        target_seq = output_seqs[0]
        
        print(f"\n分析Q{4 + variable_position - 1}三次变换:")
        print(f"输入: {input_seq}")
        print(f"目标: {target_seq}")
        print(f"第{variable_position}次变换不固定(3种选择)")
        
        if variable_position == 1:  # Q4: 第1次不固定
            print(f"第2次变换(固定): {fixed1}")
            print(f"第3次变换(固定): {fixed2}")
            
            for i, perm in enumerate(variable_options):
                intermediate1 = self.apply_permutation(input_seq, perm)
                intermediate2 = self.apply_permutation(intermediate1, fixed1)
                result = self.apply_permutation(intermediate2, fixed2)
                
                if result == target_seq:
                    print(f"\n✅ 找到正确的第1次变换!")
                    print(f"第1次变换选择 {i+1} ({perm})")
                    print(f"  {input_seq} -> {intermediate1} -> {intermediate2} -> {result}")
                    return i + 1
                    
        elif variable_position == 2:  # Q5: 第2次不固定
            print(f"第1次变换(固定): {fixed1}")
            print(f"第3次变换(固定): {fixed2}")
            
            intermediate1 = self.apply_permutation(input_seq, fixed1)
            print(f"第1次结果: {input_seq} -> {intermediate1}")
            
            for i, perm in enumerate(variable_options):
                intermediate2 = self.apply_permutation(intermediate1, perm)
                result = self.apply_permutation(intermediate2, fixed2)
                
                if result == target_seq:
                    print(f"\n✅ 找到正确的第2次变换!")
                    print(f"第2次变换选择 {i+1} ({perm})")
                    print(f"  {intermediate1} -> {intermediate2} -> {result}")
                    return i + 1
                    
        else:  # variable_position == 3, Q6: 第3次不固定
            print(f"第1次变换(固定): {fixed1}")
            print(f"第2次变换(固定): {fixed2}")
            
            intermediate1 = self.apply_permutation(input_seq, fixed1)
            intermediate2 = self.apply_permutation(intermediate1, fixed2)
            print(f"前两次结果: {input_seq} -> {intermediate1} -> {intermediate2}")
            
            for i, perm in enumerate(variable_options):
                result = self.apply_permutation(intermediate2, perm)
                
                if result == target_seq:
                    print(f"\n✅ 找到正确的第3次变换!")
                    print(f"第3次变换选择 {i+1} ({perm})")
                    print(f"  {intermediate2} -> {result}")
                    return i + 1
        
        print("\n❌ 未找到匹配的变换")
        return -1


    def run(self):
        """运行主程序"""
        self.display_menu()
        
        # 获取题型
        question_type = self.get_question_type()
        
        # 获取模式选择
        mode = self.get_mode_choice(question_type)
        
        # 获取输入输出序列
        input_seqs, output_seqs = self.get_input_output_sequences()
        
        # 根据题型决定输入方式和求解方法
        print("\n" + "="*50)
        print("求解结果:")
        print("="*50)
        
        if question_type == '1':  # Q1: 单次变换
            options = self.auto_solve_q1(input_seqs, output_seqs)
            if options is None:
                print("❌ 无法自动推导变换选项，请检查输入输出序列")
                return
            print(f"🤖 自动推导出的变换选项: {options}")
            
            answer = self.solve_q1(input_seqs, output_seqs, options)
            
            if answer > 0:
                print(f"\n最终答案: 选项 {answer} ({options[answer-1]})")
            else:
                print("\n未能找到匹配的变换")
                
        elif question_type in ['2', '3']:  # Q2-Q3: 两次变换
            if question_type == '2':
                fixed_perm = self.get_fixed_permutation("=== Q2 两次变换(第1次固定,第2次选择) ===")
            else:
                fixed_perm = self.get_fixed_permutation("=== Q3 两次变换(第2次固定,第1次选择) ===")
            
            variable_options = self.semi_auto_solve_q2_q3(input_seqs, output_seqs, question_type, fixed_perm)
            if variable_options is None:
                print("❌ 无法根据给定的固定变换推导出解，请检查输入")
                return
            
            print(f"🤖 根据固定变换推导出的可选变换: {variable_options}")
            
            answer = self.solve_q2_q3(input_seqs, output_seqs, fixed_perm, variable_options, question_type)
            
            if answer > 0:
                if question_type == '2':
                    print(f"\n最终答案: 第二次变换选项 {answer} ({variable_options[answer-1]})")
                else:
                    print(f"\n最终答案: 第一次变换选项 {answer} ({variable_options[answer-1]})")
            else:
                print("\n未能找到匹配的变换")
                
        elif question_type in ['4', '5', '6']:  # Q4-Q6: 三次变换
            variable_position = int(question_type) - 3
            
            if question_type == '4':  # Q4: 第1次可选，第2,3次固定
                fixed1 = self.get_fixed_permutation("=== Q4 第2次变换(固定) ===")
                fixed2 = self.get_fixed_permutation("=== Q4 第3次变换(固定) ===")
            elif question_type == '5':  # Q5: 第2次可选，第1,3次固定
                fixed1 = self.get_fixed_permutation("=== Q5 第1次变换(固定) ===")
                fixed2 = self.get_fixed_permutation("=== Q5 第3次变换(固定) ===")
            else:  # Q6: 第3次可选，第1,2次固定
                fixed1 = self.get_fixed_permutation("=== Q6 第1次变换(固定) ===")
                fixed2 = self.get_fixed_permutation("=== Q6 第2次变换(固定) ===")
            
            variable_options = self.semi_auto_solve_q4_q6(input_seqs, output_seqs, question_type, fixed1, fixed2)
            if variable_options is None:
                print("❌ 无法根据给定的固定变换推导出解，请检查输入")
                return
            
            print(f"🤖 根据固定变换推导出的可选变换: {variable_options}")
            
            answer = self.solve_q4_q6(input_seqs, output_seqs, fixed1, fixed2, variable_options, variable_position)
            
            if answer > 0:
                print(f"\n最终答案: 第{variable_position}次变换选项 {answer} ({variable_options[answer-1]})")
            else:
                print("\n未能找到匹配的变换")
                
        elif question_type == '7':  # Q11: 两步排列变换
            first_options, second_options = self.get_permutation_options()
            result = self.solve_two_step_permutation(input_seqs, output_seqs, first_options, second_options)
            
            if result[0] > 0 and result[1] > 0:
                print(f"\n最终答案:")
                print(f"第一步变换: 选项 {result[0]} ({first_options[result[0]-1]})")
                print(f"第二步变换: 选项 {result[1]} ({second_options[result[1]-1]})")
            else:
                print("\n未能找到匹配的排列组合")
        
        # 显示题型信息
        print(f"\n题型: {self.question_types[question_type]}")
        if question_type == '1':
            print("模式: 完全自动推导模式 🤖")
        elif question_type in ['2', '3', '4', '5', '6']:
            print("模式: 半自动推导模式 🤖")


def main():
    """主函数"""
    solver = VisualReasoningSolver()
    
    while True:
        try:
            solver.run()
            
            print("\n" + "-"*50)
                
        except KeyboardInterrupt:
            print("\n\n程序已退出")
            break
        except Exception as e:
            print(f"\n发生错误: {e}")
            print("请重新开始")


if __name__ == "__main__":
    main()
