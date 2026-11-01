import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FeatureCatalog } from "@/components/feature-catalog";

describe("FeatureCatalog", () => {
  it("renders catalog", () => {
    const { container } = render(
      <FeatureCatalog total={10} gaPct={90} modules={["core", "security"]}
        features={[
          { name: "Extension SDK", status: "ga", module: "core" },
          { name: "Multi-Region", status: "beta", module: "infra" },
        ]} />
    );
    expect(container.textContent).toContain("Feature Catalog");
    expect(container.textContent).toContain("10 features");
    expect(container.textContent).toContain("90% GA");
    expect(container.textContent).toContain("Extension SDK");
    expect(container.textContent).toContain("ga");
    expect(container.textContent).toContain("beta");
  });
});
