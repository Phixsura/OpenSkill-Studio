import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InfraDriftPanel } from "@/components/infra-drift-panel";
describe("InfraDriftPanel", () => {
  it("renders drift", () => {
    const { container } = render(
      <InfraDriftPanel hasDrift={true} totalIssues={3}
        missing={["vm-2"]} extra={["vm-3"]}
        drifted={[{ resource: "vm-1", changes: { cpu: { desired: 4, actual: 8 } } }]} />
    );
    expect(container.textContent).toContain("Infrastructure Drift");
    expect(container.textContent).toContain("3 issues");
    expect(container.textContent).toContain("missing: vm-2");
    expect(container.textContent).toContain("extra: vm-3");
    expect(container.textContent).toContain("vm-1");
    expect(container.textContent).toContain("cpu");
  });
});
