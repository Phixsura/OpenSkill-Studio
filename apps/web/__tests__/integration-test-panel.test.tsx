import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { IntegrationTestPanel } from "@/components/integration-test-panel";

const tests = [
  { name: "test_install", scenario: "Install flow", outcome: "pass" as const, durationMs: 500 },
  { name: "test_webhook", scenario: "Webhook flow", outcome: "fail" as const, durationMs: 1000, error: "Timeout" },
];
const report = { total: 2, passed: 1, failed: 1, passRate: 50, durationMs: 1500 };

describe("IntegrationTestPanel", () => {
  it("renders tests and report", () => {
    const { container } = render(<IntegrationTestPanel tests={tests} report={report} />);
    expect(container.textContent).toContain("test_install");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("1500ms");
  });
  it("calls onRun", () => {
    const fn = vi.fn();
    const { getByText } = render(<IntegrationTestPanel tests={[]} report={report} onRun={fn} />);
    fireEvent.click(getByText("Run Suite"));
    expect(fn).toHaveBeenCalled();
  });
});
