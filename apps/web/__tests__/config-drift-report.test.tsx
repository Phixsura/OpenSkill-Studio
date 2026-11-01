import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConfigDriftReport } from "@/components/config-drift-report";

describe("ConfigDriftReport", () => {
  it("renders drifts", () => {
    const { container } = render(
      <ConfigDriftReport totalDrifts={2} severity="warning" byType={{ changed: 1, extra: 1, missing: 0 }}
        diffs={[
          { path: "replicas", type: "changed", expected: 3, actual: 2 },
          { path: "env.DEBUG", type: "extra", expected: null, actual: "true" },
        ]} />
    );
    expect(container.textContent).toContain("Config Drift");
    expect(container.textContent).toContain("2 drifts");
    expect(container.textContent).toContain("replicas");
    expect(container.textContent).toContain("changed");
    expect(container.textContent).toContain("- 3");
    expect(container.textContent).toContain("+ 2");
  });
});
