'''
Hypothesis失败用例复现脚本
运行此脚本可以复现Hypothesis发现的失败用例
'''
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import Record, Tag

def reproduce_failure(failure_id, input_data, expected_error=None):
    print(f"\n=== 复现失败用例 #{failure_id} ===")
    print(f"输入数据: {input_data}")
    
    try:
        # 解析输入数据
        in_or_out = input_data.get('in_or_out', True)
        amount = input_data.get('amount', 100)
        
        # 处理标签
        tag_value = input_data.get('tag', '工资')
        tag = None
        for t in Tag:
            if t.value == tag_value:
                tag = t
                break
        
        if tag is None:
            tag = Tag.SALARY
        
        time_str = input_data.get('time', '2024-01-01 12:00')
        custom_tag = input_data.get('custom_text', input_data.get('custom_tag', ''))
        
        # 创建Record
        record = Record(
            in_or_out=in_or_out,
            number=amount,
            tag=tag,
            time=time_str,
            custom_tag=custom_tag
        )
        
        # 尝试显示
        text = record.get_display_text()
        print(f"✅ 成功: {text[:50]}...")
        return False
        
    except Exception as e:
        print(f"❌ 失败: {type(e).__name__}: {e}")
        if expected_error and expected_error in str(e):
            print(f"✅ 符合预期错误: {expected_error}")
        return True

print("开始复现Hypothesis发现的失败用例...")

# 失败用例 #1
reproduce_failure(
    failure_id=1,
    input_data={'in_or_out': True, 'amount': -1000, 'tag': '工资', 'time': '2022-06-31 17:22', 'custom_text': ''},
    expected_error="failed to satisfy assume() in test_record_property_based (line 72)"
)

# 失败用例 #2
reproduce_failure(
    failure_id=2,
    input_data={'in_or_out': True, 'amount': -1000, 'tag': '工资', 'time': '2022-06-31 00:22', 'custom_text': ''},
    expected_error="failed to satisfy assume() in test_record_property_based (line 72)"
)

# 失败用例 #3
reproduce_failure(
    failure_id=3,
    input_data={'in_or_out': True, 'amount': -1000, 'tag': '工资', 'time': '2022-06-31 00:00', 'custom_text': ''},
    expected_error="failed to satisfy assume() in test_record_property_based (line 72)"
)

print('\n所有失败用例复现完成！')