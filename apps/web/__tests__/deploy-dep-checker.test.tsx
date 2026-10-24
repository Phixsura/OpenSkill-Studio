import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployDepChecker } from "@/components/deploy-dep-checker";

describe("DeployDepChecker", () => {
  it("renders", () => {
    const { container } = render(
      <DeployDepChecker service="api" canDeploy={false} passed={1} total={2} blocking={1}
        prerequisites={[
          { name: "tests", type: "ci", status: "ready", passed: true, required: true },
          { name: "security", type: "scan", status: "failed", passed: false, required: true },
        ]} />
    );
    expect(container.textContent).toContain("Deploy Check: api");
    expect(container.textContent).toContain("1 blocking");
    expect(container.textContent).toContain("1/2");
    expect(container.textContent).toContain("tests");
    expect(container.textContent).toContain("security");
    expect(container.textContent).toContain("required");
  });
});
