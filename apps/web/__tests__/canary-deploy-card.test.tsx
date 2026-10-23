import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CanaryDeployCard } from "@/components/canary-deploy-card";

describe("CanaryDeployCard", () => {
  it("renders canary", () => {
    const { container } = render(
      <CanaryDeployCard service="api" baseline="2.0" canary="2.1" trafficPct={25}
        phase="expanding" status="running" healthy={true}
        onAdvance={vi.fn()} onRollback={vi.fn()} onPromote={vi.fn()} />
    );
    expect(container.textContent).toContain("Canary: api");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("v2.1");
    expect(container.textContent).toContain("25%");
    expect(container.textContent).toContain("expanding");
    expect(container.textContent).toContain("Advance");
    expect(container.textContent).toContain("Rollback");
  });
});
