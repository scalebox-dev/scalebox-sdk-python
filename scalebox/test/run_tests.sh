#!/bin/bash

# ScaleBox 沙箱验证测试运行脚本
# 这个脚本提供了一个简单的方式来运行所有验证测试

set -e  # 出错时立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python环境
check_python_env() {
    print_info "检查Python环境..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        exit 1
    fi
    
    # 检查必要的模块是否可以导入
    if ! python3 -c "import sys; sys.path.insert(0, '/home/ubuntu/git_home/scalebox'); import scalebox" 2>/dev/null; then
        print_warning "ScaleBox模块路径可能有问题，但继续尝试运行测试"
    else
        print_success "Python环境检查通过"
    fi
}

# 运行单个测试
run_single_test() {
    local test_name=$1
    local description=$2
    
    print_info "开始运行: $description"
    echo "========================================================"
    
    if python3 "$test_name"; then
        print_success "$description 完成"
        return 0
    else
        print_error "$description 失败"
        return 1
    fi
}

# 显示使用帮助
show_help() {
    echo "ScaleBox 沙箱验证测试运行脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help              显示此帮助信息"
    echo "  -a, --async-only        仅运行异步测试"
    echo "  -s, --sync-only         仅运行同步测试"
    echo "  -S, --stress-only       仅运行压力测试"
    echo "  -u, --usage-only        仅运行使用示例"
    echo "  -q, --quick             快速测试（跳过压力测试）"
    echo "  -v, --verbose           详细输出"
    echo ""
    echo "示例:"
    echo "  $0                      运行所有测试"
    echo "  $0 --async-only         仅运行异步测试"
    echo "  $0 --quick              运行除压力测试外的所有测试"
    echo ""
}

# 主函数
main() {
    local run_async=true
    local run_sync=true
    local run_stress=true
    local run_usage=true
    local verbose=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -a|--async-only)
                run_sync=false
                run_stress=false
                run_usage=false
                shift
                ;;
            -s|--sync-only)
                run_async=false
                run_stress=false
                run_usage=false
                shift
                ;;
            -S|--stress-only)
                run_async=false
                run_sync=false
                run_usage=false
                shift
                ;;
            -u|--usage-only)
                run_async=false
                run_sync=false
                run_stress=false
                shift
                ;;
            -q|--quick)
                run_stress=false
                shift
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            *)
                print_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 设置详细输出
    if [ "$verbose" = true ]; then
        set -x
    fi
    
    print_info "ScaleBox 沙箱验证测试开始"
    print_info "开始时间: $(date)"
    
    # 检查环境
    check_python_env
    
    # 切换到测试目录
    cd "$(dirname "$0")"
    
    local total_tests=0
    local failed_tests=0
    local start_time=$(date +%s)
    
    # 运行异步测试
    if [ "$run_async" = true ]; then
        ((total_tests++))
        if ! run_single_test "test_sandbox_async_comprehensive.py" "AsyncSandbox 综合功能验证"; then
            ((failed_tests++))
        fi
        echo ""
    fi
    
    # 运行同步测试
    if [ "$run_sync" = true ]; then
        ((total_tests++))
        if ! run_single_test "test_sandbox_sync_comprehensive.py" "Sandbox 综合功能验证"; then
            ((failed_tests++))
        fi
        echo ""
    fi
    
    # 运行压力测试
    if [ "$run_stress" = true ]; then
        ((total_tests++))
        print_warning "压力测试可能需要较长时间..."
        if ! run_single_test "test_sandbox_stress_and_edge_cases.py" "压力测试和边界条件验证"; then
            ((failed_tests++))
        fi
        echo ""
    fi
    
    # 运行使用示例
    if [ "$run_usage" = true ]; then
        ((total_tests++))
        if ! run_single_test "test_sandbox_usage_examples.py" "使用示例和最佳实践演示"; then
            ((failed_tests++))
        fi
        echo ""
    fi
    
    # 生成最终报告
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo "========================================================"
    print_info "ScaleBox 沙箱验证测试 - 最终报告"
    echo "========================================================"
    
    print_info "测试统计:"
    echo "  总测试套件: $total_tests"
    echo "  成功套件: $((total_tests - failed_tests))"
    echo "  失败套件: $failed_tests"
    
    if [ $total_tests -gt 0 ]; then
        local success_rate=$(( (total_tests - failed_tests) * 100 / total_tests ))
        echo "  成功率: ${success_rate}%"
    fi
    
    echo "  总耗时: ${duration}秒"
    echo "  完成时间: $(date)"
    
    # 根据结果设置退出状态
    if [ $failed_tests -eq 0 ]; then
        print_success "所有测试都通过了！"
        exit 0
    else
        print_error "有 $failed_tests 个测试套件失败"
        exit 1
    fi
}

# 运行主函数
main "$@"
