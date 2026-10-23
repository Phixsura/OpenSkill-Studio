import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TestPipelineResults } from "@/components/test-pipeline-results";

describe("TestPipelineResults", () => {
  const suites = [{ name: "Unit", passed: 50, failed: 0, skipped: 2, total: 52, duration_ms: 3000, status: "passed" }];
  const summary = { passed: 50, failed: 0, skipped: 2, total: 52 };
  it("renders", () => {
    const { container } = render(
      <TestPipelineResults suites={suites} summary={summary} allPassed={true} publishable={true} onPublish={vi.fn()} />
    );
    expect(container.textContent).toContain("Test Results");
    expect(container.textContent).toContain("All Passed");
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain("Publish App");
  });
  it("publish", () => {
    const fn = vi.fn();
    const { container } = render(
      <TestPipelineResults suites={suites} summary={summary} allPassed={true} publishable={true} onPublish={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Publish App")!);
    expect(fn).toHaveBeenCalled();
  });
});
