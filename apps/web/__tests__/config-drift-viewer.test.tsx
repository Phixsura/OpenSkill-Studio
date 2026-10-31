import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConfigDriftViewer } from "@/components/config-drift-viewer";

describe("ConfigDriftViewer", () => {
  it("renders", () => {
    const { container } = render(
      <ConfigDriftViewer baseline="prod" driftedCount={1}
        comparisons={{
          staging: { drifted: true, severity: "warning", missing: [], extra: [],
            changed: [{ key: "db", expected: "prod-db", actual: "stg-db" }], totalIssues: 1 },
        }} />
    );
    expect(container.textContent).toContain("Config Drift");
    expect(container.textContent).toContain("vs prod");
    expect(container.textContent).toContain("1 drifted");
    expect(container.textContent).toContain("staging");
    expect(container.textContent).toContain("warning");
  });
});
