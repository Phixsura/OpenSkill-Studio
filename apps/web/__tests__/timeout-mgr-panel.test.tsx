import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TimeoutMgrPanel } from "@/components/timeout-mgr-panel";
describe("TimeoutMgrPanel", () => {
  it("renders", () => {
    const { container } = render(
      <TimeoutMgrPanel defaultMs={5000} timeoutsHit={42}
        endpoints={[
          { endpoint: "/api/reports", timeoutMs: 30000 },
          { endpoint: "/api/export", timeoutMs: 60000 },
        ]} />
    );
    expect(container.textContent).toContain("Timeout Manager");
    expect(container.textContent).toContain("default: 5000ms");
    expect(container.textContent).toContain("42 timeouts");
    expect(container.textContent).toContain("/api/reports");
    expect(container.textContent).toContain("30000ms");
  });
});
