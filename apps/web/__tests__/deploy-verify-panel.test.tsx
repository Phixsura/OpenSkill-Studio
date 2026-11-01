import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployVerifyPanel } from "@/components/deploy-verify-panel";
describe("DeployVerifyPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DeployVerifyPanel success={false} verdict="verification_failed" passed={1} total={2}
        checks={[
          { check: "health_check", status: "pass", durationMs: 50, message: "" },
          { check: "smoke_test", status: "fail", durationMs: 5000, message: "timeout" },
        ]} />
    );
    expect(container.textContent).toContain("VERIFICATION FAILED");
    expect(container.textContent).toContain("1/2 passed");
    expect(container.textContent).toContain("health_check");
    expect(container.textContent).toContain("smoke_test");
    expect(container.textContent).toContain("timeout");
  });
});
