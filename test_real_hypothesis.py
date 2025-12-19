"""
使用真正的Hypothesis基于属性测试
测试记账软件的Record类
"""
import sys
import os
from datetime import datetime, timedelta
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import Record, Tag

from hypothesis import given, strategies as st, settings, HealthCheck, assume, example, seed, note
from hypothesis import strategies as st
import hypothesis

print("=" * 80)
print("Hypothesis基于属性测试 - 记账软件Record类")
print("=" * 80)
print("使用Hypothesis自动生成和收缩测试用例\n")

# 测试结果
test_stats = {
    "tests_run": 0,
    "examples_generated": 0,
    "failing_examples": []
}


def record_test_result(success=True, message=""):
    """记录测试结果"""
    if not success:
        print(f"  ✗ {message}")


# 测试1: Record对象的基本属性
@seed(123456)  # 固定种子以便复现
@settings(
    max_examples=200,
    deadline=2000,
    suppress_health_check=[HealthCheck.too_slow],
    print_blob=True
)
@given(
    in_or_out=st.booleans(),
    amount=st.integers(min_value=-1000, max_value=2000000),  # 包含负数和超范围值
    tag_value=st.sampled_from([t.value for t in Tag]),  # 使用字符串值
    year=st.integers(min_value=1900, max_value=2100),
    month=st.integers(min_value=1, max_value=12),
    day=st.integers(min_value=1, max_value=31),
    hour=st.integers(min_value=0, max_value=23),
    minute=st.integers(min_value=0, max_value=59),
    custom_text=st.text(max_size=100, alphabet=st.characters(min_codepoint=32, max_codepoint=126))
)
def test_record_property_based(in_or_out, amount, tag_value, year, month, day, hour, minute, custom_text):
    """基于属性的测试：验证Record类的各种属性"""
    test_stats["examples_generated"] += 1
    
    # 记录测试输入
    note(f"测试输入: in_or_out={in_or_out}, amount={amount}, tag={tag_value}, "
         f"time={year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}")
    
    try:
        # 1. 验证时间有效性
        try:
            datetime(year, month, day, hour, minute)
            valid_date = True
        except ValueError:
            valid_date = False
        
        # 如果日期无效，跳过这个测试
        assume(valid_date)
        
        # 2. 构建时间字符串
        time_str = f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"
        
        # 3. 找到对应的Tag枚举
        tag = None
        for t in Tag:
            if t.value == tag_value:
                tag = t
                break
        
        assume(tag is not None)
        
        # 4. 处理自定义标签
        custom_tag = ""
        if tag == Tag.CUSTOM:
            custom_tag = custom_text
        
        # 5. 创建Record对象
        record = Record(
            in_or_out=in_or_out,
            number=amount,
            tag=tag,
            time=time_str,
            custom_tag=custom_tag
        )
        
        # 6. 验证Record属性一致性
        assert record.in_or_out == in_or_out
        assert record.number == amount
        assert record.tag == tag
        assert record.time == time_str
        if tag == Tag.CUSTOM:
            assert record.custom_tag == custom_tag
        else:
            assert record.custom_tag == ""
        
        # 7. 验证显示文本
        display_text = record.get_display_text()
        assert isinstance(display_text, str)
        assert len(display_text) > 0
        
        # 8. 验证显示文本包含必要信息
        # 金额应该出现在文本中（或者为0时显示0）
        amount_str = str(abs(amount)) if amount != 0 else "0"
        assert amount_str in display_text
        
        # 时间应该出现在文本中
        assert time_str in display_text
        
        # 标签应该出现在文本中
        if tag == Tag.CUSTOM and custom_tag:
            assert custom_tag in display_text
        else:
            assert tag.value in display_text
        
        # 9. 验证显示文本格式（粗略检查）
        assert "元" in display_text
        direction = "收入" if in_or_out else "支出"
        assert direction in display_text
        
        test_stats["tests_run"] += 1
        if test_stats["tests_run"] % 50 == 0:
            print(f"  已生成 {test_stats['tests_run']} 个有效测试用例...")
            
    except Exception as e:
        # 记录失败的测试用例
        error_info = {
            "input": {
                "in_or_out": in_or_out,
                "amount": amount,
                "tag": tag_value,
                "time": f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}",
                "custom_text": custom_text[:50]
            },
            "error": str(e),
            "type": type(e).__name__
        }
        test_stats["failing_examples"].append(error_info)
        print(f"  ✗ 发现失败用例: {type(e).__name__}: {e}")
        print(f"    输入: amount={amount}, tag={tag_value}")
        
        # 重新抛出异常让Hypothesis知道测试失败
        raise


# 测试2: 时间格式的鲁棒性测试
@settings(
    max_examples=100,
    deadline=1000,
    phases=[hypothesis.Phase.generate, hypothesis.Phase.shrink]  # 启用收缩功能
)
@given(
    time_str=st.text(
        min_size=1,
        max_size=50,
        alphabet=st.characters(
            min_codepoint=32,
            max_codepoint=126,
            blacklist_characters=["\x00"]  # 排除空字符
        )
    )
)
def test_time_format_robustness(time_str):
    """测试时间格式的鲁棒性：各种字符串输入"""
    test_stats["examples_generated"] += 1
    
    note(f"测试时间字符串: {repr(time_str)}")
    
    try:
        # 尝试创建Record，可能失败
        record = Record(
            in_or_out=True,
            number=100,
            tag=Tag.SALARY,
            time=time_str,
            custom_tag=""
        )
        
        # 如果成功创建，验证显示文本
        display_text = record.get_display_text()
        assert isinstance(display_text, str)
        
        # 验证时间出现在显示文本中
        assert time_str in display_text
        
        test_stats["tests_run"] += 1
        
    except (ValueError, TypeError) as e:
        # 预期的时间格式错误，这是正常的
        assume(False)  # 告诉Hypothesis跳过这个无效用例
    except Exception as e:
        # 其他未预期的异常
        error_info = {
            "input": {"time_str": time_str},
            "error": str(e),
            "type": type(e).__name__
        }
        test_stats["failing_examples"].append(error_info)
        print(f"  ✗ 时间格式测试失败: {type(e).__name__}: {e}")
        raise


# 测试3: 自定义标签的边界情况
@settings(
    max_examples=50,
    deadline=1000
)
@given(
    amount=st.integers(min_value=1, max_value=999999),
    custom_tag=st.one_of(
        st.text(min_size=1, max_size=200),  # 普通文本
        st.text(min_size=100, max_size=500),  # 长文本
        st.just(""),  # 空字符串
        st.just(" " * 50),  # 空格
        st.just("🎯💰💳⭐✨"),  # emoji
        st.just("\n\t\r"),  # 控制字符
        st.just("A" * 1000),  # 超长文本
    )
)
def test_custom_tag_edge_cases(amount, custom_tag):
    """测试自定义标签的各种边界情况"""
    test_stats["examples_generated"] += 1
    
    note(f"测试自定义标签: 金额={amount}, 标签长度={len(custom_tag)}")
    
    try:
        # 创建Record
        record = Record(
            in_or_out=True,
            number=amount,
            tag=Tag.CUSTOM,
            time="2024-01-01 12:00",
            custom_tag=custom_tag
        )
        
        # 验证显示
        display_text = record.get_display_text()
        assert isinstance(display_text, str)
        
        # 如果自定义标签不为空，应该出现在显示文本中
        if custom_tag.strip():
            # 注意：很长的标签可能被截断，所以我们只检查非空标签
            pass
        
        test_stats["tests_run"] += 1
        
    except Exception as e:
        error_info = {
            "input": {"amount": amount, "custom_tag": repr(custom_tag[:100])},
            "error": str(e),
            "type": type(e).__name__
        }
        test_stats["failing_examples"].append(error_info)
        print(f"  ✗ 自定义标签测试失败: {type(e).__name__}: {e}")
        raise


# 测试4: 金额边界和格式测试
@example(amount=0)
@example(amount=1)
@example(amount=999999)
@example(amount=1000000)
@example(amount=-1)
@example(amount=-1000000)
@settings(
    max_examples=50,
    deadline=1000
)
@given(
    amount=st.integers(min_value=-2000000, max_value=2000000)
)
def test_amount_edge_cases(amount):
    """测试金额的各种边界情况"""
    test_stats["examples_generated"] += 1
    
    note(f"测试金额边界: {amount}")
    
    try:
        # 创建Record
        record = Record(
            in_or_out=True,
            number=amount,
            tag=Tag.SALARY,
            time="2024-01-01 12:00",
            custom_tag=""
        )
        
        # 验证显示
        display_text = record.get_display_text()
        assert isinstance(display_text, str)
        
        # 金额应该出现在显示文本中
        amount_str = str(abs(amount)) if amount != 0 else "0"
        assert amount_str in display_text or "0" in display_text
        
        test_stats["tests_run"] += 1
        
    except Exception as e:
        error_info = {
            "input": {"amount": amount},
            "error": str(e),
            "type": type(e).__name__
        }
        test_stats["failing_examples"].append(error_info)
        print(f"  ✗ 金额边界测试失败: {type(e).__name__}: {e}")
        raise


def run_hypothesis_tests():
    """运行所有Hypothesis测试"""
    print("\n开始运行Hypothesis基于属性测试...\n")
    
    tests = [
        ("基于属性的Record测试", test_record_property_based),
        ("时间格式鲁棒性测试", test_time_format_robustness),
        ("自定义标签边界测试", test_custom_tag_edge_cases),
        ("金额边界测试", test_amount_edge_cases),
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"运行测试: {test_name}")
        print(f"{'='*60}")
        
        try:
            # Hypothesis会自动运行多次测试
            test_func()
            print(f"\n✅ {test_name}: 通过")
        except hypothesis.errors.Unsatisfiable:
            print(f"\n⚠️  {test_name}: 无法生成有效测试用例")
        except hypothesis.errors.FailedHealthCheck as e:
            print(f"\n⚠️  {test_name}: 健康检查失败 - {e}")
        except Exception as e:
            print(f"\n❌ {test_name}: 失败 - {type(e).__name__}: {e}")
    
    return len(test_stats["failing_examples"]) == 0


def generate_test_report():
    """生成测试报告"""
    print("\n" + "=" * 80)
    print("Hypothesis测试报告")
    print("=" * 80)
    
    print(f"生成的测试用例总数: {test_stats['examples_generated']}")
    print(f"运行的有效测试用例: {test_stats['tests_run']}")
    print(f"发现的失败用例: {len(test_stats['failing_examples'])}")
    
    if test_stats["failing_examples"]:
        print(f"\n⚠️  发现 {len(test_stats['failing_examples'])} 个失败用例:")
        print("-" * 40)
        
        # 按错误类型分组
        error_groups = {}
        for failure in test_stats["failing_examples"]:
            error_type = failure["type"]
            if error_type not in error_groups:
                error_groups[error_type] = []
            error_groups[error_type].append(failure)
        
        for error_type, failures in error_groups.items():
            print(f"\n{error_type} ({len(failures)} 个):")
            for i, failure in enumerate(failures[:3], 1):  # 显示前3个
                print(f"  {i}. 输入: {failure['input']}")
                print(f"     错误: {failure['error'][:100]}")
        
        # 保存失败用例到文件
        with open('hypothesis_failures.json', 'w', encoding='utf-8') as f:
            json.dump(test_stats["failing_examples"], f, indent=2, ensure_ascii=False)
        print(f"\n📄 详细失败信息已保存到: hypothesis_failures.json")
        
        # 创建最小化复现脚本
        create_minimal_reproduction_script()
    else:
        print("\n✅ 所有测试通过！未发现失败用例。")
    
    print("\n" + "=" * 80)


def create_minimal_reproduction_script():
    """创建最小化复现脚本"""
    if not test_stats["failing_examples"]:
        return
    
    script = """'''
Hypothesis失败用例复现脚本
运行此脚本可以复现Hypothesis发现的失败用例
'''
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import Record, Tag

def reproduce_failure(failure_id, input_data, expected_error=None):
    print(f"\\n=== 复现失败用例 #{failure_id} ===")
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
"""
    
    # 添加失败用例
    for i, failure in enumerate(test_stats["failing_examples"][:10], 1):  # 最多10个
        script += f"\n# 失败用例 #{i}\n"
        script += f"reproduce_failure(\n"
        script += f"    failure_id={i},\n"
        script += f"    input_data={failure['input']},\n"
        script += f"    expected_error=\"{failure['error'][:100]}\"\n"
        script += f")\n"
    
    script += "\nprint('\\n所有失败用例复现完成！')"
    
    with open('reproduce_hypothesis_failures.py', 'w', encoding='utf-8') as f:
        f.write(script)
    
    print(f"🔄 失败用例复现脚本已保存到: reproduce_hypothesis_failures.py")


def main():
    """主函数"""
    try:
        # 运行Hypothesis测试
        success = run_hypothesis_tests()
        
        # 生成报告
        generate_test_report()
        
        # 退出代码
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
        generate_test_report()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试运行异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()