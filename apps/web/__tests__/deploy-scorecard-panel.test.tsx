import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployScorecardPanel } from "@/components/deploy-scorecard-panel";
describe("DeployScorecardPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DeployScorecardPanel version="2.0" score={100} grade="A" deployReady={true}
        dimensions={{ tests: 25, security: 20, canary: 15, rollback: 10, monitoring: 15, review: 15 }} />
    );
    expect(container.textContent).toContain("100/100 — A");
    expect(container.textContent).toContain("2.0");
    expect(container.textContent).toContain("Deploy Ready");
    expect(container.textContent).toContain("tests");
    expect(container.textContent).toContain("25pts");
    expect(container.textContent).toContain("security");
  });
});
