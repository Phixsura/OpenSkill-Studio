import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ContentScanReport } from "@/components/content-scan-report";

const FAILED_RESULT = {
  app_id: "app-1",
  passed: false,
  findings: [
    {
      category: "secret_leak" as const,
      severity: "critical" as const,
      message: "API key detected",
      file_path: "config.py",
      line_number: 5,
      pattern_matched: "API key",
    },
    {
      category: "unsafe_code" as const,
      severity: "high" as const,
      message: "eval() usage",
      file_path: "handler.py",
      line_number: 12,
      pattern_matched: "eval()",
    },
    {
      category: "invalid_url" as const,
      severity: "medium" as const,
      message: "Localhost URL",
      file_path: "settings.json",
      line_number: 3,
      pattern_matched: null,
    },
  ],
  files_scanned: 15,
  total_bytes: 245000,
};

const PASSED_RESULT = {
  app_id: "app-2",
  passed: true,
  findings: [],
  files_scanned: 8,
  total_bytes: 32000,
};

describe("ContentScanReport", () => {
  it("renders heading and app name", () => {
    const { container } = render(<ContentScanReport result={FAILED_RESULT} appName="Bad App" />);
    expect(container.textContent).toContain("Content Scan Report");
    expect(container.textContent).toContain("Bad App");
  });

  it("renders file count and size", () => {
    const { container } = render(<ContentScanReport result={FAILED_RESULT} appName="App" />);
    expect(container.textContent).toContain("15 files");
    expect(container.textContent).toContain("239.3 KB");
  });

  it("shows Failed badge", () => {
    const { container } = render(<ContentScanReport result={FAILED_RESULT} appName="App" />);
    expect(container.textContent).toContain("Failed");
  });

  it("shows Passed badge", () => {
    const { container } = render(<ContentScanReport result={PASSED_RESULT} appName="App" />);
    expect(container.textContent).toContain("Passed");
  });

  it("renders finding count summary", () => {
    const { container } = render(<ContentScanReport result={FAILED_RESULT} appName="App" />);
    expect(container.textContent).toContain("3 findings");
    expect(container.textContent).toContain("1 critical");
    expect(container.textContent).toContain("1 high");
  });

  it("renders severity badges", () => {
    const { container } = render(<ContentScanReport result={FAILED_RESULT} appName="App" />);
    expect(container.textContent).toContain("CRITICAL");
    expect(container.textContent).toContain("HIGH");
    expect(container.textContent).toContain("MEDIUM");
  });

  it("renders finding messages", () => {
    const { container } = render(<ContentScanReport result={FAILED_RESULT} appName="App" />);
    expect(container.textContent).toContain("API key detected");
    expect(container.textContent).toContain("Localhost URL");
  });

  it("renders category labels", () => {
    const { container } = render(<ContentScanReport result={FAILED_RESULT} appName="App" />);
    expect(container.textContent).toContain("Secret Leak");
    expect(container.textContent).toContain("Unsafe Code");
    expect(container.textContent).toContain("Invalid URL");
  });

  it("renders file paths and line numbers", () => {
    const { container } = render(<ContentScanReport result={FAILED_RESULT} appName="App" />);
    expect(container.textContent).toContain("config.py:5");
    expect(container.textContent).toContain("handler.py:12");
  });

  it("shows clean scan empty state", () => {
    const { container } = render(<ContentScanReport result={PASSED_RESULT} appName="App" />);
    expect(container.textContent).toContain("clean scan");
  });

  it("renders severity icons", () => {
    const { container } = render(<ContentScanReport result={FAILED_RESULT} appName="App" />);
    expect(container.textContent).toContain("🔴");
    expect(container.textContent).toContain("🟠");
    expect(container.textContent).toContain("🟡");
  });
});
