import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TestSuiteRunnerCard } from "@/components/test-suite-runner-card";

describe("TestSuiteRunnerCard", () => {
  it("renders results", () => {
    const results = [
      { name: "health", passed: true, duration_ms: 50, actual_status: 200 },
      { name: "auth", passed: false, duration_ms: 100, actual_status: 401 },
    ];
    const { container } = render(
      <TestSuiteRunnerCard name="Smoke Tests" results={results} passRate={50} totalMs={150} onRerun={vi.fn()} />
    );
    expect(container.textContent).toContain("Smoke Tests");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("health");
    expect(container.textContent).toContain("auth");
  });
  it("rerun", () => {
    const fn = vi.fn();
    const { container } = render(
      <TestSuiteRunnerCard name="X" results={[]} passRate={100} totalMs={0} onRerun={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Run"))!);
    expect(fn).toHaveBeenCalled();
  });
});
