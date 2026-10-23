import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusIndicatorDot } from "@/components/status-indicator-dot";

describe("StatusIndicatorDot", () => {
  it("renders operational", () => {
    const { container } = render(
      <StatusIndicatorDot status="operational" label="Operational" icon="🟢" />
    );
    expect(container.textContent).toContain("🟢");
    expect(container.textContent).toContain("Operational");
  });
  it("renders with counts", () => {
    const { container } = render(
      <StatusIndicatorDot status="degraded" label="Degraded" icon="🟡"
        healthyCount={3} totalCount={5} />
    );
    expect(container.textContent).toContain("🟡");
    expect(container.textContent).toContain("3/5 healthy");
  });
  it("hides label", () => {
    const { container } = render(
      <StatusIndicatorDot status="operational" label="Op" icon="🟢" showLabel={false} />
    );
    expect(container.textContent).not.toContain("Op");
  });
});
