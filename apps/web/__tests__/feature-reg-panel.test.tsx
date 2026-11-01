import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FeatureRegPanel } from "@/components/feature-reg-panel";

describe("FeatureRegPanel", () => {
  it("renders", () => {
    const { container } = render(
      <FeatureRegPanel enabled={2} total={3}
        features={[
          { name: "dark_mode", enabled: true, description: "Dark theme", owner: "ui-team", tags: ["ui"] },
          { name: "new_api", enabled: true, description: "", owner: "api-team", tags: ["api"] },
          { name: "beta_feature", enabled: false, description: "Beta", owner: "", tags: ["beta"] },
        ]} />
    );
    expect(container.textContent).toContain("Feature Registry");
    expect(container.textContent).toContain("2/3 enabled");
    expect(container.textContent).toContain("dark_mode");
    expect(container.textContent).toContain("Dark theme");
    expect(container.textContent).toContain("ui");
    expect(container.textContent).toContain("beta");
  });
});
