#!/usr/bin/env python
"""
运行集成测试
"""
import sys
import os
import pytest

def main():
    """运行集成测试"""
    # 添加项目根目录到Python路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    print("=" * 60)
    print("开始运行集成测试")
    print("=" * 60)
    
    # 运行集成测试
    test_dir = os.path.join(project_root, "tests", "integration")
    
    print("\n1. 运行自底向上集成测试...")
    result1 = pytest.main(["-v", os.path.join(test_dir, "test_bottom_up.py")])
    
    print("\n2. 运行混合集成测试...")
    result2 = pytest.main(["-v", os.path.join(test_dir, "test_mixed_integration.py")])
    
    print("\n3. 运行端到端场景测试...")
    result3 = pytest.main(["-v", os.path.join(test_dir, "test_end_to_end.py")])
    
    print("\n" + "=" * 60)
    print("集成测试完成")
    print("=" * 60)
    
    # 返回测试结果
    if result1 == 0 and result2 == 0 and result3 == 0:
        print("✅ 所有集成测试通过！")
        return 0
    else:
        print("❌ 部分集成测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())