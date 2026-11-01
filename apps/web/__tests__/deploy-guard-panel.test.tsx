import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeployGuardPanel } from "@/components/deploy-guard-panel";

describe("DeployGuardPanel", () => {
  it("renders guards", () => {
    const { container } = render(
      <DeployGuardPanel canDeploy={false} passed={3} total={4} onDeploy={vi.fn()}
        guards={[
          { guard: "tests", description: "Tests passing", blocking: true, passed: true },
          { guard: "vulns", description: "No vulnerabilities", blocking: true, passed: false },
          { guard: "approval", description: "Approved", blocking: true, passed: true },
          { guard: "budget", description: "Perf budget", blocking: false, passed: true },
        ]} />
    );
    expect(container.textContent).toContain("Deploy Guards");
    expect(container.textContent).toContain("3/4 passed");
    expect(container.textContent).toContain("Blocked");
    expect(container.textContent).toContain("Tests passing");
    expect(container.textContent).toContain("blocking");
  });
});
