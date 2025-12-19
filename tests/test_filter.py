"""
数据筛选功能的单元测试
"""
import pytest
import sys
import os

# 手动添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import Record, Tag


class TestFilterFunction:
    """测试筛选功能"""
    
    @pytest.fixture
    def sample_records(self):
        """创建测试数据"""
        return [
            Record(True, 1000, Tag.SALARY, "2024-01-10 09:00"),
            Record(False, 200, Tag.FOOD, "2024-01-10 12:00"),
            Record(True, 500, Tag.AWARD, "2024-01-11 10:00"),
            Record(False, 1500, Tag.HOUSE, "2024-01-12 15:00"),
            Record(False, 50, Tag.TRAFFIC, "2024-01-13 08:00"),
            Record(True, 300, Tag.CUSTOM, "2024-01-14 14:00", "兼职"),
            Record(False, 800, Tag.CLOTHES, "2024-01-15 16:00"),
        ]
    
    def test_filter_no_conditions(self, qtbot, sample_records):
        """测试无筛选条件"""
        from main import AccountingApp
        
        # 使用qtbot来管理窗口
        app_window = AccountingApp()
        qtbot.addWidget(app_window)  # 让pytest-qt管理窗口
        app_window.records = sample_records
        
        filtered = app_window.filter_records()
        assert len(filtered) == 7
    
    def test_filter_min_amount(self, qtbot, sample_records):
        """测试最小金额筛选"""
        from main import AccountingApp
        
        app_window = AccountingApp()
        qtbot.addWidget(app_window)
        app_window.records = sample_records
        app_window.min_amount_input.setText("500")
        
        filtered = app_window.filter_records()
        assert len(filtered) == 4
    
    def test_filter_max_amount(self, qtbot, sample_records):
        """测试最大金额筛选"""
        from main import AccountingApp
        
        app_window = AccountingApp()
        qtbot.addWidget(app_window)
        app_window.records = sample_records
        app_window.max_amount_input.setText("300")
        
        filtered = app_window.filter_records()
        assert len(filtered) == 3
    
    def test_filter_both_min_max(self, qtbot, sample_records):
        """测试同时设置最小和最大金额"""
        from main import AccountingApp
        
        app_window = AccountingApp()
        qtbot.addWidget(app_window)
        app_window.records = sample_records
        app_window.min_amount_input.setText("200")
        app_window.max_amount_input.setText("800")
        
        filtered = app_window.filter_records()
        assert len(filtered) == 4
    
    def test_filter_empty_records(self, qtbot):
        """测试空记录列表"""
        from main import AccountingApp
        
        app_window = AccountingApp()
        qtbot.addWidget(app_window)
        app_window.records = []
        
        filtered = app_window.filter_records()
        assert len(filtered) == 0
    
    def test_filter_single_record(self, qtbot):
        """测试单条记录"""
        from main import AccountingApp
        
        app_window = AccountingApp()
        qtbot.addWidget(app_window)
        app_window.records = [Record(True, 100, Tag.SALARY)]
        
        # 包含该记录
        app_window.min_amount_input.setText("50")
        filtered = app_window.filter_records()
        assert len(filtered) == 1
        
        # 不包含该记录
        app_window.min_amount_input.setText("200")
        filtered = app_window.filter_records()
        assert len(filtered) == 0
    
    def test_filter_invalid_input(self, qtbot, sample_records):
        """测试无效输入"""
        from main import AccountingApp
        
        app_window = AccountingApp()
        qtbot.addWidget(app_window)
        app_window.records = sample_records
        
        # 非数字输入
        app_window.min_amount_input.setText("abc")
        filtered = app_window.filter_records()
        assert len(filtered) == 7
        
        # 负数输入
        app_window.min_amount_input.setText("-100")
        filtered = app_window.filter_records()
        assert len(filtered) == 7