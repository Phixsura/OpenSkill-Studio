import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CanaryAnalysisReport } from "@/components/canary-analysis-report";

describe("CanaryAnalysisReport", () => {
  const checks = [
    { metric: "error_rate", passed: true, baseline: 0.1, canary: 0.2 },
    { metric: "p95_latency", passed: false, baseline: 100, canary: 300 },
  ];
  it("renders", () => {
    const { container } = render(
      <CanaryAnalysisReport verdict="rollback" checks={checks} confidence={50}
        onPromote={vi.fn()} onRollback={vi.fn()} />
    );
    expect(container.textContent).toContain("Canary Analysis");
    expect(container.textContent).toContain("Rollback Recommended");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("❌");
  });
  it("rollback", () => {
    const fn = vi.fn();
    const { container } = render(
      <CanaryAnalysisReport verdict="rollback" checks={checks} confidence={50}
        onPromote={vi.fn()} onRollback={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Rollback")!);
    expect(fn).toHaveBeenCalled();
  });
});
