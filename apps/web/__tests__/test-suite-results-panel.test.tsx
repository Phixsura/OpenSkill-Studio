import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TestSuiteResultsPanel } from "@/components/test-suite-results-panel";

describe("TestSuiteResultsPanel", () => {
  const checks = [
    { name: "has_name", passed: true, message: "App name is required" },
    { name: "has_icon", passed: false, message: "App icon is required" },
  ];
  it("renders", () => {
    const { container } = render(
      <TestSuiteResultsPanel checks={checks} score={50} readyToPublish={false} onPublish={vi.fn()} />
    );
    expect(container.textContent).toContain("Pre-Publish Tests");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("✗");
    expect(container.textContent).toContain("Fix issues");
  });
  it("publish when ready", () => {
    const fn = vi.fn();
    const { container } = render(
      <TestSuiteResultsPanel checks={[checks[0]]} score={100} readyToPublish={true} onPublish={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Publish App")!);
    expect(fn).toHaveBeenCalled();
  });
});
