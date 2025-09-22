#!/bin/bash

# Code Interpreter 测试运行脚本

echo "=========================================="
echo "Code Interpreter 测试套件"
echo "=========================================="

# 检查Python版本
echo "🐍 Python版本:"
python3 --version

echo ""
echo "📋 可用的测试选项:"
echo "1. 简单同步测试 (testcodeinterpreter_sync.py)"
echo "2. 简单异步测试 (testcodeinterpreter_async.py)"
echo "3. 综合同步测试 (test_code_interpreter_sync_comprehensive.py)"
echo "4. 综合异步测试 (test_code_interpreter_async_comprehensive.py)"
echo "5. 运行所有测试"
echo ""

# 询问用户选择
echo "请选择要运行的测试 (1-5)，或按 Enter 运行简单同步测试："
read choice

case $choice in
    1)
        echo "🚀 运行简单同步测试..."
        python3 testcodeinterpreter_sync.py
        ;;
    2)
        echo "🚀 运行简单异步测试..."
        python3 testcodeinterpreter_async.py
        ;;
    3)
        echo "🚀 运行综合同步测试..."
        python3 test_code_interpreter_sync_comprehensive.py
        ;;
    4)
        echo "🚀 运行综合异步测试..."
        python3 test_code_interpreter_async_comprehensive.py
        ;;
    5)
        echo "🚀 运行所有测试..."
        echo ""
        echo "--- 简单同步测试 ---"
        python3 testcodeinterpreter_sync.py
        echo ""
        echo "--- 简单异步测试 ---"
        python3 testcodeinterpreter_async.py
        echo ""
        echo "--- 综合同步测试 ---"
        python3 test_code_interpreter_sync_comprehensive.py
        echo ""
        echo "--- 综合异步测试 ---"
        python3 test_code_interpreter_async_comprehensive.py
        ;;
    *)
        echo "🚀 运行默认的简单同步测试..."
        python3 testcodeinterpreter_sync.py
        ;;
esac

echo ""
echo "=========================================="
echo "测试完成！"
echo "=========================================="
