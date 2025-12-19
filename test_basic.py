"""
基础测试文件
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import Record, Tag

def test_record_creation():
    """测试Record创建"""
    record = Record(True, 1000, Tag.SALARY, "2024-01-01 12:00", "")
    assert record.in_or_out is True
    assert record.number == 1000
    assert record.tag == Tag.SALARY
    return True

def test_record_display():
    """测试显示文本"""
    record = Record(False, 500, Tag.FOOD, "2024-01-01 12:30", "午餐")
    text = record.get_display_text()
    assert "支出" in text
    assert "500元" in text
    return True

def run_all_tests():
    """运行所有测试"""
    tests = [test_record_creation, test_record_display]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_func.__name__}: 通过")
                passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__}: 失败 - {e}")
            failed += 1
    
    print(f"\n测试结果: 通过 {passed}, 失败 {failed}")
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)