package main

import (
    "bufio"
    "bytes"
    "context"
    "flag"
    "fmt"
    "os"
    "os/exec"
    "path/filepath"
    "regexp"
    "runtime"
    "strings"
    "sync"
    "time"
)

// Defaults
const (
    repoRoot = "/root/scalebox"
    testFile = repoRoot + "/test/test_code_interpreter_sync_comprehensive.py"
)

var (
    // success rate 0% detection: 支持全角/半角冒号与百分号，0 / 0.0 / 0.00
    reZeroRate = regexp.MustCompile(`成功率\s*[：:]\s*0(?:\.0+)?\s*[％%]`)

    reTotal = regexp.MustCompile(`总测试数\s*[：:]\s*(\d+)`)
    reFail  = regexp.MustCompile(`失败数\s*[：:]\s*(\d+)`)

    // sandbox id extraction
    reSandboxExplicit = []*regexp.Regexp{
        regexp.MustCompile(`sandbox[_\s-]*id\s*[:=]\s*([A-Za-z0-9_\-]+)`),
        regexp.MustCompile(`Sandbox[_\s-]*ID\s*[:=]\s*([A-Za-z0-9_\-]+)`),
        regexp.MustCompile(`sandbox\s*:\s*([A-Za-z0-9_\-]+)`),
        regexp.MustCompile(`sandboxId\s*[:=]\s*([A-Za-z0-9_\-]+)`),
    }
    reUUID  = regexp.MustCompile(`\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b`)
    reSbxID = regexp.MustCompile(`\bsbx_[A-Za-z0-9]+\b`)
)

type runResult struct {
    id       int
    duration time.Duration
    pass     bool
    report   string
}

func extractFinalReport(text string) string {
    lines := strings.Split(text, "\n")
    if len(lines) == 0 {
        return ""
    }
    // Prefer last title containing CodeInterpreter + 测试报告
    titleIdx := -1
    for i, line := range lines {
        if strings.Contains(line, "CodeInterpreter") && strings.Contains(line, "测试报告") {
            titleIdx = i
        }
    }
    if titleIdx >= 0 {
        return strings.TrimSpace(strings.Join(lines[titleIdx:], "\n"))
    }
    // Fallback: last long ===== block
    sepIdx := -1
    for i, line := range lines {
        s := strings.TrimSpace(line)
        if len(s) >= 20 {
            onlyEq := true
            for _, r := range s {
                if r != '=' {
                    onlyEq = false
                    break
                }
            }
            if onlyEq {
                sepIdx = i
            }
        }
    }
    if sepIdx >= 0 {
        return strings.TrimSpace(strings.Join(lines[sepIdx:], "\n"))
    }
    return strings.TrimSpace(text)
}

func extractSandboxID(text string) string {
    for _, re := range reSandboxExplicit {
        if m := re.FindStringSubmatch(text); len(m) == 2 {
            return m[1]
        }
    }
    if m := reUUID.FindString(text); m != "" {
        return m
    }
    if m := reSbxID.FindString(text); m != "" {
        return m
    }
    return ""
}

func analyzeReport(stdoutText, stderrText string, exitCode int) (pass bool, report string) {
    report = extractFinalReport(stdoutText)
    if report == "" {
        report = extractFinalReport(stderrText)
    }
    if report == "" {
        // Fallback to last 10 lines of either
        tail := func(s string) string {
            lines := strings.Split(strings.TrimSpace(s), "\n")
            if len(lines) > 10 {
                lines = lines[len(lines)-10:]
            }
            return strings.Join(lines, "\n")
        }
        joined := stdoutText
        if joined == "" {
            joined = stderrText
        }
        report = tail(joined)
    }

    combined := report + "\n" + stdoutText + "\n" + stderrText
    pass = (exitCode == 0)

    zeroRate := reZeroRate.FindStringIndex(combined) != nil
    if !zeroRate {
        // parse totals fallback
        totalM := reTotal.FindStringSubmatch(combined)
        failM := reFail.FindStringSubmatch(combined)
        if len(totalM) == 2 && len(failM) == 2 {
            // if parsing fails, ignore
            var totalN, failN int
            fmt.Sscanf(totalM[1], "%d", &totalN)
            fmt.Sscanf(failM[1], "%d", &failN)
            if totalN > 0 && failN == totalN {
                zeroRate = true
            }
        }
    }

    if zeroRate {
        pass = false
        // Attach more detail
        var b strings.Builder
        b.WriteString(report)
        sandboxID := extractSandboxID(combined)
        if sandboxID != "" {
            b.WriteString("\n\nSandbox ID: ")
            b.WriteString(sandboxID)
        }
        if stderrText != "" {
            b.WriteString("\n[stderr]\n")
            b.WriteString(stderrText)
        }
        if stdoutText != "" {
            b.WriteString("\n[stdout]\n")
            b.WriteString(stdoutText)
        }
        report = b.String()
    }
    return
}

func runOnce(ctx context.Context, id int) runResult {
    start := time.Now()

    // Use the same Python that runs in PATH
    cmd := exec.CommandContext(ctx, "python3", testFile)
    cmd.Dir = repoRoot

    var stdoutBuf, stderrBuf bytes.Buffer
    cmd.Stdout = &stdoutBuf
    cmd.Stderr = &stderrBuf

    _ = cmd.Run()

    duration := time.Since(start)
    stdoutText := stdoutBuf.String()
    stderrText := stderrBuf.String()
    pass, report := analyzeReport(stdoutText, stderrText, cmd.ProcessState.ExitCode())

    return runResult{
        id:       id,
        duration: duration,
        pass:     pass,
        report:   report,
    }
}

func main() {
    // Tune GOMAXPROCS to available CPUs (8c recommended by user)
    runtime.GOMAXPROCS(runtime.NumCPU())

    var (
        concurrency int
        perTestTimeoutSec int
    )
    flag.IntVar(&concurrency, "concurrency", 1000, "number of concurrent runs")
    flag.IntVar(&perTestTimeoutSec, "timeout", 600, "per test timeout seconds")
    flag.Parse()

    if concurrency <= 0 {
        fmt.Println("concurrency must be > 0")
        os.Exit(2)
    }

    // Pre-flight checks
    if _, err := os.Stat(testFile); err != nil {
        fmt.Printf("Test file not found: %s\n", testFile)
        os.Exit(2)
    }

    // Print basic info
    abs, _ := filepath.Abs(testFile)
    fmt.Printf("Running %d concurrent tests against %s\n", concurrency, abs)

    // We'll launch N goroutines. Each has its own context with timeout.
    // Printing is serialized to avoid interleaving lines.
    outMu := &sync.Mutex{}

    ctx := context.Background()
    overallStart := time.Now()
    var wg sync.WaitGroup
    results := make(chan runResult, concurrency)

    for i := 1; i <= concurrency; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            c, cancel := context.WithTimeout(ctx, time.Duration(perTestTimeoutSec)*time.Second)
            defer cancel()
            res := runOnce(c, id)
            results <- res
        }(i)
    }

    // Close results when done
    go func() {
        wg.Wait()
        close(results)
    }()

    // Consume results as they arrive, print progressively
    completed := 0
    passed := 0
    failed := 0

    writer := bufio.NewWriter(os.Stdout)
    for r := range results {
        completed++
        if r.pass {
            passed++
        } else {
            failed++
        }
        outMu.Lock()
        fmt.Fprintf(writer, "Run %03d: %s in %.2fs\n", r.id, ternary(r.pass, "PASS", "FAIL"), r.duration.Seconds())
        if r.report != "" {
            fmt.Fprintln(writer, r.report)
            fmt.Fprintln(writer, strings.Repeat("-", 64))
        }
        writer.Flush()
        outMu.Unlock()
    }

    totalTime := time.Since(overallStart).Seconds()
    fmt.Println(strings.Repeat("-", 64))
    fmt.Printf("Completed: %d, Passed: %d, Failed: %d, Total time: %.2fs\n", completed, passed, failed, totalTime)
}

func ternary[T any](cond bool, a, b T) T {
    if cond {
        return a
    }
    return b
}


