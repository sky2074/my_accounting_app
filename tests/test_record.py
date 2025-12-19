"""
Record类的单元测试
"""
import pytest
from datetime import datetime
import sys
import os

# 手动添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import Record, Tag


class TestRecord:
    """测试Record类"""
    
    def test_record_creation_default_time(self):
        """测试使用默认时间创建记录"""
        record = Record(True, 1000, Tag.SALARY)
        assert record.in_or_out is True
        assert record.number == 1000
        assert record.tag == Tag.SALARY
        assert record.custom_tag == ""
        # 验证时间格式
        assert isinstance(record.time, str)
        datetime.strptime(record.time, "%Y-%m-%d %H:%M")
    
    def test_record_creation_custom_time(self):
        """测试使用自定义时间创建记录"""
        custom_time = "2024-01-15 14:30"
        record = Record(False, 50, Tag.FOOD, custom_time)
        assert record.time == custom_time
    
    def test_record_creation_custom_tag(self):
        """测试使用自定义标签创建记录"""
        record = Record(True, 500, Tag.CUSTOM, custom_tag="兼职收入")
        assert record.tag == Tag.CUSTOM
        assert record.custom_tag == "兼职收入"
    
    def test_get_display_text_income(self):
        """测试收入记录的显示文本"""
        record = Record(True, 1000, Tag.SALARY, "2024-01-15 14:30")
        text = record.get_display_text()
        assert "收入" in text
        assert "1000元" in text
        assert Tag.SALARY.value in text
    
    def test_get_display_text_expense(self):
        """测试支出记录的显示文本"""
        record = Record(False, 200, Tag.FOOD, "2024-01-15 14:30")
        text = record.get_display_text()
        assert "支出" in text
        assert "200元" in text
        assert Tag.FOOD.value in text
    
    def test_get_display_text_custom_tag(self):
        """测试自定义标签的显示文本"""
        record = Record(True, 300, Tag.CUSTOM, "2024-01-15 14:30", "稿费")
        text = record.get_display_text()
        assert "稿费" in text
    
    def test_record_equality(self):
        """测试记录比较"""
        time = "2024-01-15 14:30"
        record1 = Record(True, 1000, Tag.SALARY, time)
        record2 = Record(True, 1000, Tag.SALARY, time)
        record3 = Record(False, 1000, Tag.SALARY, time)
        
        # 相同时间、类型、金额应该显示相同
        assert record1.get_display_text() == record2.get_display_text()
        # 不同类型应该不同
        assert record1.get_display_text() != record3.get_display_text()
    
    def test_record_with_zero_amount(self):
        """测试边界金额（接近0）"""
        record = Record(True, 1, Tag.SALARY)  # 最小正金额
        text = record.get_display_text()
        assert "1元" in text
    
    def test_record_large_amount(self):
        """测试大金额处理"""
        record = Record(True, 999999, Tag.SALARY)
        text = record.get_display_text()
        assert "999999元" in text
    
    def test_record_negative_amount_error(self):
        """测试负数金额（应该由调用者处理验证）"""
        # Record类本身不验证金额，金额验证应该在UI层
        # 这里测试它是否能接受负数（虽然不应该）
        record = Record(True, -100, Tag.SALARY)
        assert record.number == -100
    
    def test_all_tags_display(self):
        """测试所有标签的显示"""
        tags_to_test = [
            (Tag.SALARY, "工资"),
            (Tag.AWARD, "奖金"),
            (Tag.FOOD, "食物"),
            (Tag.CLOTHES, "衣物"),
            (Tag.HOUSE, "住房"),
            (Tag.TRAFFIC, "交通"),
        ]
        
        for tag, expected_text in tags_to_test:
            record = Record(True, 100, tag, "2024-01-15 14:30")
            text = record.get_display_text()
            assert expected_text in text