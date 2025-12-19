"""
混合集成测试
测试不同模块之间的交互
"""
import pytest
import sys
import os
from datetime import datetime
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import Record, Tag, AccountingApp


class TestMixedIntegration:
    """混合集成测试"""
    
    def test_data_flow_integration(self):
        """测试数据流集成：从Record创建到显示的全过程"""
        # 创建测试数据
        test_records = [
            Record(True, 3000, Tag.SALARY, "2024-01-10 09:00", "基本工资"),
            Record(False, 1500, Tag.HOUSE, "2024-01-11 10:00", "房租"),
            Record(False, 200, Tag.FOOD, "2024-01-12 12:00", "午餐"),
            Record(True, 500, Tag.CUSTOM, "2024-01-13 14:00", "奖金"),
        ]
        
        # 验证数据
        assert len(test_records) == 4
        assert test_records[0].number == 3000
        assert test_records[1].tag == Tag.HOUSE
        assert test_records[2].custom_tag == "午餐"
        assert test_records[3].in_or_out is True
        
        # 验证每条记录都能正确显示
        for record in test_records:
            text = record.get_display_text()
            assert "元" in text
            assert record.time in text
    
    def test_filter_sort_integration(self, qtbot):
          """测试筛选和排序的集成"""
          app = AccountingApp()
          qtbot.addWidget(app)
    
          app.records = [
              Record(True, 500, Tag.SALARY, "2024-01-15 14:30"),
              Record(False, 1000, Tag.HOUSE, "2024-01-10 10:00"),
              Record(True, 200, Tag.AWARD, "2024-01-20 09:00"),
              Record(False, 300, Tag.FOOD, "2024-01-05 12:00"),
              Record(True, 800, Tag.CUSTOM, "2024-01-25 16:00", "兼职"),
          ]
    
          # 设置筛选和排序
          app.sort_combo.setCurrentIndex(1)  # 按金额排序
          app.sort_order_combo.setCurrentIndex(0)  # 升序
          app.min_amount_input.setText("300")
    
          # 触发排序和筛选
          app.auto_sort_and_filter()
    
          # 验证显示列表中的内容（跳过表头）
          displayed_amounts = []
          for i in range(1, app.record_list.count()):  # i=0是表头
              item_text = app.record_list.item(i).text()
              # 从文本中提取金额
              import re
              match = re.search(r'(\d+)\s*元', item_text)
              if match:
                  displayed_amounts.append(int(match.group(1)))
    
          print("显示列表中的金额:", displayed_amounts)
    
          # 应该显示按金额升序排列的筛选结果
          assert displayed_amounts == [300, 500, 800, 1000]


    def test_balance_filter_integration(self, qtbot):
        """测试余额计算与筛选的集成"""
        app = AccountingApp()
        qtbot.addWidget(app)
        
        current_month = datetime.now().strftime("%Y-%m")
        
        # 创建测试数据 - 使用当前月份
        app.records = [
            Record(True, 5000, Tag.SALARY, f"{current_month}-01 09:00"),
            Record(False, 2000, Tag.HOUSE, f"{current_month}-05 10:00"),
            Record(False, 1000, Tag.FOOD, f"{current_month}-10 12:00"),
            Record(True, 800, Tag.AWARD, f"{current_month}-15 14:00"),
            # 超出筛选范围的记录
            Record(True, 300, Tag.CUSTOM, f"{current_month}-20 16:00", "小费"),
        ]
        
        # 先计算原始余额
        app.update_balance()
        original_balance = app.balance_label.text()
        
        # 总收入：5000 + 800 + 300 = 6100
        # 总支出：2000 + 1000 = 3000
        # 结余：3100
        assert "收入6100元" in original_balance
        assert "支出3000元" in original_balance
        assert "= 3100元" in original_balance
        
        # 应用筛选（只显示>=500的记录）
        app.min_amount_input.setText("500")
        app.auto_sort_and_filter()
        
        # 筛选后余额应该不变（余额计算不受筛选影响）
        app.update_balance()
        filtered_balance = app.balance_label.text()
        assert filtered_balance == original_balance
        
        # 验证显示列表减少但余额不变
        # 筛选后应该显示4条记录（300被过滤掉）
        filtered = app.filter_records()
        assert len(filtered) == 4
    
    def test_error_handling_integration(self, qtbot):
        """测试错误处理的集成"""
        app = AccountingApp()
        qtbot.addWidget(app)
        
        # 准备测试数据
        app.records = [
            Record(True, 1000, Tag.SALARY, "2024-01-10 09:00"),
            Record(False, 500, Tag.FOOD, "2024-01-11 12:00"),
        ]
        
        # 测试无效输入的处理集成
        app.min_amount_input.setText("invalid")
        app.max_amount_input.setText("also_invalid")
        
        # 应该忽略无效输入，显示所有记录
        filtered = app.filter_records()
        assert len(filtered) == 2
        
        # 清除无效输入
        app.clear_filter()
        assert app.min_amount_input.text() == ""
        assert app.max_amount_input.text() == ""
        
        # 测试部分有效输入
        app.min_amount_input.setText("300")      # 有效
        app.max_amount_input.setText("not_num")  # 无效
        
        filtered = app.filter_records()
        assert len(filtered) == 2  # 只应用有效的最小值筛选
        
        # 验证余额计算在无效数据下的表现
        app.update_balance()
        # 应该正常计算，不崩溃
    
    def test_performance_integration(self, qtbot):
        """测试性能相关的集成"""
        app = AccountingApp()
        qtbot.addWidget(app)
        
        # 创建大量测试数据
        app.records = []
        current_month = datetime.now().strftime("%Y-%m")
        
        for i in range(50):  # 50条记录（避免太多）
            is_income = i % 3 == 0
            amount = (i + 1) * 100
            tag = Tag.SALARY if is_income else Tag.FOOD
            time = f"{current_month}-{(i%30)+1:02d} {(i%24):02d}:{(i%60):02d}"
            
            app.records.append(Record(is_income, amount, tag, time))
        
        # 测试筛选性能
        import time
        start_time = time.time()
        
        app.min_amount_input.setText("5000")
        app.max_amount_input.setText("8000")
        filtered = app.filter_records()
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # 验证性能可接受
        assert elapsed < 1.0  # 应该在1秒内完成
        
        # 验证筛选结果正确
        for record in filtered:
            assert 5000 <= record.number <= 8000