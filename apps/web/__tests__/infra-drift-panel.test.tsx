import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InfraDriftPanel } from "@/components/infra-drift-panel";

describe("InfraDriftPanel", () => {
  it("renders", () => {
    const { container } = render(
      <InfraDriftPanel hasDrift={true} driftedCount={2} totalResources={5} driftPct={40}
        drifts={[
          { key: "replicas", desired: 3, actual: 5, type: "changed" },
          { key: "memory", desired: "4Gi", actual: null, type: "missing" },
        ]} />
    );
    expect(container.textContent).toContain("Infrastructure Drift");
    expect(container.textContent).toContain("2/5 drifted");
    expect(container.textContent).toContain("40%");
    expect(container.textContent).toContain("replicas");
    expect(container.textContent).toContain("changed");
    expect(container.textContent).toContain("memory");
  });
});
