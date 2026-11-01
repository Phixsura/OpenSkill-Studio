import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AlertSuppressionPanel } from "@/components/alert-suppression-panel";

describe("AlertSuppressionPanel", () => {
  it("renders rules", () => {
    const { container } = render(
      <AlertSuppressionPanel activeCount={1} totalSuppressed={15} onAdd={vi.fn()}
        rules={[
          { id: 1, name: "deploy-silence", pattern: "deploy.*", reason: "Deploying", suppressedCount: 10, active: true },
          { id: 2, name: "old-rule", pattern: "test.*", reason: "Testing", suppressedCount: 5, active: false },
        ]} />
    );
    expect(container.textContent).toContain("Alert Suppression");
    expect(container.textContent).toContain("1 active");
    expect(container.textContent).toContain("15 suppressed");
    expect(container.textContent).toContain("deploy-silence");
    expect(container.textContent).toContain("deploy.*");
  });
});
