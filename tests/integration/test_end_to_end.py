"""
端到端场景测试
模拟真实用户使用场景
"""
import pytest
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import Record, Tag, AccountingApp


class TestEndToEndScenarios:
    """端到端场景测试"""
    
    def test_scenario1_monthly_accounting(self, qtbot):
        """场景1：月度记账流程"""
        app = AccountingApp()
        qtbot.addWidget(app)
        
        from datetime import datetime
        current_month = datetime.now().strftime("%Y-%m")
        
        # 模拟一个月的记账数据 - 使用当前月份
        monthly_records = [
            # 工资收入
            Record(True, 8000, Tag.SALARY, f"{current_month}-05 09:00", "基本工资"),
            Record(True, 1000, Tag.AWARD, f"{current_month}-10 14:00", "绩效奖金"),
            
            # 固定支出
            Record(False, 3000, Tag.HOUSE, f"{current_month}-01 10:00", "房租"),
            Record(False, 500, Tag.TRAFFIC, f"{current_month}-03 08:00", "交通费"),
            
            # 日常消费
            Record(False, 200, Tag.FOOD, f"{current_month}-02 12:00", "午餐"),
            Record(False, 150, Tag.FOOD, f"{current_month}-04 19:00", "晚餐"),
            Record(False, 300, Tag.CLOTHES, f"{current_month}-06 15:00", "衣服"),
            Record(False, 100, Tag.CUSTOM, f"{current_month}-08 20:00", "电影"),
        ]
        
        app.records = monthly_records
        
        # 步骤1：查看本月总览
        app.update_balance()
        balance_text = app.balance_label.text()
        assert "收入9000元" in balance_text  # 8000 + 1000
        assert "支出4250元" in balance_text  # 3000 + 500 + 200 + 150 + 300 + 100
        assert "= 4750元" in balance_text    # 结余

    
    def test_scenario2_expense_analysis(self, qtbot):
        """场景2：支出分析场景"""
        app = AccountingApp()
        qtbot.addWidget(app)
        
        # 模拟支出分析场景
        app.records = [
            Record(False, 2000, Tag.HOUSE, "2024-01-01 10:00", "房租"),
            Record(False, 500, Tag.TRAFFIC, "2024-01-02 08:00", "地铁"),
            Record(False, 300, Tag.FOOD, "2024-01-02 12:00", "午餐"),
            Record(False, 1500, Tag.HOUSE, "2024-01-03 14:00", "水电费"),
            Record(False, 200, Tag.FOOD, "2024-01-03 19:00", "晚餐"),
            Record(False, 800, Tag.CLOTHES, "2024-01-04 15:00", "外套"),
            Record(False, 100, Tag.TRAFFIC, "2024-01-05 09:00", "公交"),
            Record(False, 400, Tag.FOOD, "2024-01-05 20:00", "聚餐"),
        ]
        
        # 场景：找出高额支出（>1000）
        app.min_amount_input.setText("1000")
        high_expenses = app.filter_records()
        assert len(high_expenses) == 2  # 房租和水电费
        
        # 场景：分析每日饮食预算（假设每天不超过200）
        app.clear_filter()
        app.min_amount_input.setText("200")
        app.max_amount_input.setText("500")
        filtered = app.filter_records()
        
        # 找出超标的饮食消费
        food_over_budget = [r for r in filtered 
                          if r.tag == Tag.FOOD or "餐" in r.custom_tag]
        # 300和400的餐饮消费超标
        assert len(food_over_budget) >= 1
        
        # 场景：查看交通总支出
        app.clear_filter()
        app.max_amount_input.setText("600")
        filtered = app.filter_records()
        traffic_expenses = [r for r in filtered 
                          if r.tag == Tag.TRAFFIC or "交通" in r.custom_tag]
        # 500+100=600
        assert len(traffic_expenses) == 2
    
    def test_scenario3_income_expense_comparison(self, qtbot):
        """场景3：收支对比场景"""
        app = AccountingApp()
        qtbot.addWidget(app)
        
        from datetime import datetime
        current_month = datetime.now().strftime("%Y-%m")
        
        # 模拟收支对比场景 - 使用当前月份
        app.records = [
            # 收入
            Record(True, 8000, Tag.SALARY, f"{current_month}-05 09:00"),
            Record(True, 2000, Tag.AWARD, f"{current_month}-15 14:00"),
            Record(True, 500, Tag.CUSTOM, f"{current_month}-20 16:00", "兼职"),
            
            # 支出
            Record(False, 3000, Tag.HOUSE, f"{current_month}-01 10:00"),
            Record(False, 1000, Tag.TRAFFIC, f"{current_month}-03 08:00"),
            Record(False, 2000, Tag.FOOD, f"{current_month}-10 12:00"),
            Record(False, 1500, Tag.CLOTHES, f"{current_month}-12 15:00"),
            Record(False, 500, Tag.CUSTOM, f"{current_month}-25 20:00", "娱乐"),
        ]
        
        # 计算收支比例
        app.update_balance()
        balance_text = app.balance_label.text()
        
        # 总收入：8000 + 2000 + 500 = 10500
        # 总支出：3000 + 1000 + 2000 + 1500 + 500 = 8000
        # 结余：2500
        
        assert "收入10500元" in balance_text
        assert "支出8000元" in balance_text
        assert "= 2500元" in balance_text
        
        # 分析：找出哪些支出类别可以削减
        # 先看大额支出（>1500）
        app.min_amount_input.setText("1500")
        large_expenses = app.filter_records()
        # >=1500 的记录: 8000, 2000, 3000, 2000, 1500 共5条
        assert len(large_expenses) == 5
        
    def test_scenario4_data_recovery_and_consistency(self, qtbot):
        """场景4：数据恢复和一致性测试"""
        app = AccountingApp()
        qtbot.addWidget(app)
        
        # 创建复杂的数据集
        complex_records = []
        
        # 添加各种类型的记录
        for i in range(20):
            record_type = i % 4
            
            if record_type == 0:  # 工资收入
                rec = Record(True, 5000 + (i * 100), Tag.SALARY, 
                           f"2024-01-{(i%30)+1:02d} 09:00", f"工资{i}")
            elif record_type == 1:  # 日常支出
                rec = Record(False, 100 + (i * 10), Tag.FOOD,
                           f"2024-01-{(i%30)+1:02d} 12:00", f"餐费{i}")
            elif record_type == 2:  # 固定支出
                rec = Record(False, 1000 + (i * 50), Tag.HOUSE,
                           f"2024-01-{(i%30)+1:02d} 10:00", f"账单{i}")
            else:  # 其他收入
                rec = Record(True, 300 + (i * 20), Tag.CUSTOM,
                           f"2024-01-{(i%30)+1:02d} 15:00", f"其他{i}")
            
            complex_records.append(rec)
        
        app.records = complex_records
        
        # 执行一系列操作
        operations = [
            ("filter", "500", ""),      # 筛选>=500
            ("sort", "amount", "desc"), # 按金额降序
            ("filter", "", "2000"),     # 筛选<=2000
            ("clear", "", ""),          # 清除筛选
            ("sort", "time", "asc"),    # 按时间升序
        ]
        
        # 执行操作并验证数据一致性
        total_amount_before = sum(r.number for r in app.records)
        
        for op_type, param1, param2 in operations:
            if op_type == "filter":
                app.min_amount_input.setText(param1)
                app.max_amount_input.setText(param2)
                app.auto_sort_and_filter()
            elif op_type == "sort":
                if param1 == "amount":
                    app.sort_combo.setCurrentIndex(1)
                else:
                    app.sort_combo.setCurrentIndex(0)
                
                if param2 == "desc":
                    app.sort_order_combo.setCurrentIndex(1)
                else:
                    app.sort_order_combo.setCurrentIndex(0)
                
                app.auto_sort_and_filter()
            elif op_type == "clear":
                app.clear_filter()
                app.auto_sort_and_filter()
            
            # 验证数据完整性：总金额应该不变
            filtered_records = app.filter_records()
            current_total = sum(r.number for r in filtered_records)
            
            # 注意：筛选会影响当前显示的总金额
            # 但原始数据的总金额应该不变
            original_total = sum(r.number for r in app.records)
            assert original_total == total_amount_before
        
        # 最终验证：清除所有筛选后应该恢复原始状态
        app.clear_filter()
        app.sort_combo.setCurrentIndex(0)
        app.sort_order_combo.setCurrentIndex(0)
        app.auto_sort_and_filter()
        
        assert len(app.filter_records()) == len(complex_records)
        assert app.min_amount_input.text() == ""
        assert app.max_amount_input.text() == ""