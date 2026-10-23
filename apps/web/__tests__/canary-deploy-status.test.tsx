import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CanaryDeployStatus } from "@/components/canary-deploy-status";

describe("CanaryDeployStatus", () => {
  it("renders canary", () => {
    const onAdvance = vi.fn();
    const { container, getByText } = render(
      <CanaryDeployStatus appId="myapp" version="2.0" phase="canary"
        trafficPct={20} checksCount={3} onAdvance={onAdvance} onRollback={vi.fn()} />
    );
    expect(container.textContent).toContain("Canary Deploy");
    expect(container.textContent).toContain("myapp");
    expect(container.textContent).toContain("20%");
    expect(container.textContent).toContain("canary");
    fireEvent.click(getByText("Advance"));
    expect(onAdvance).toHaveBeenCalled();
  });
});
