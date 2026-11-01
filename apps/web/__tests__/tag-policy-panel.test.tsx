import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TagPolicyPanel } from "@/components/tag-policy-panel";

describe("TagPolicyPanel", () => {
  it("renders", () => {
    const { container } = render(
      <TagPolicyPanel total={5} compliant={3} nonCompliant={2} compliancePct={60}
        violations={[{ resource: "db", missingTags: ["cost_center", "managed_by"] }]} />
    );
    expect(container.textContent).toContain("Tag Policy");
    expect(container.textContent).toContain("60% compliant");
    expect(container.textContent).toContain("3/5");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("cost_center, managed_by");
  });
});
