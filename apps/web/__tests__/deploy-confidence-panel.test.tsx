import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployConfidencePanel } from "@/components/deploy-confidence-panel";
describe("DeployConfidencePanel", () => {
  it("renders", () => {
    const { container } = render(
      <DeployConfidencePanel score={92} level="high"
        factors={{ tests: 25, coverage: 13, security: 20, canary: 20, review: 10, rollback: 4 }} />
    );
    expect(container.textContent).toContain("92/100");
    expect(container.textContent).toContain("HIGH CONFIDENCE");
    expect(container.textContent).toContain("tests");
    expect(container.textContent).toContain("25");
    expect(container.textContent).toContain("security");
    expect(container.textContent).toContain("20");
  });
});
