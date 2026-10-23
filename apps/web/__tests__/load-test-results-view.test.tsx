import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LoadTestResultsView } from "@/components/load-test-results-view";

describe("LoadTestResultsView", () => {
  const results = { total_requests: 600, successful: 594, failed: 6, actual_rps: 20,
    p50_ms: 55, p95_ms: 160, p99_ms: 317, error_rate: 1.0 };
  it("renders", () => {
    const { container } = render(
      <LoadTestResultsView testId="lt_1" endpoint="/api/apps" concurrentUsers={50}
        results={results} verdict="pass" onRerun={vi.fn()} />
    );
    expect(container.textContent).toContain("Load Test Results");
    expect(container.textContent).toContain("pass");
    expect(container.textContent).toContain("600");
    expect(container.textContent).toContain("160ms");
  });
  it("rerun", () => {
    const fn = vi.fn();
    const { container } = render(
      <LoadTestResultsView testId="lt_1" endpoint="/api" concurrentUsers={50}
        results={results} verdict="pass" onRerun={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Re-run Test")!);
    expect(fn).toHaveBeenCalled();
  });
});
