import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InfraTagCompliance } from "@/components/infra-tag-compliance";

describe("InfraTagCompliance", () => {
  it("renders compliance", () => {
    const { container } = render(
      <InfraTagCompliance compliancePct={50} compliant={1} nonCompliant={1}
        results={[
          { resource: "api", compliant: true, missing: [], tagCount: 4 },
          { resource: "db", compliant: false, missing: ["team", "cost_center"], tagCount: 1 },
        ]} />
    );
    expect(container.textContent).toContain("Tag Compliance");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("1 compliant");
    expect(container.textContent).toContain("1 non-compliant");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("team, cost_center");
  });
});
