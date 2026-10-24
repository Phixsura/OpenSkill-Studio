import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FeatureFlagPanel } from "@/components/feature-flag-panel";

describe("FeatureFlagPanel", () => {
  it("renders", () => {
    const { container } = render(
      <FeatureFlagPanel userId="u1" enabledCount={2}
        flags={[
          { flag: "dark_mode", value: true, reason: "rollout" },
          { flag: "beta_ui", value: true, reason: "allowlisted" },
          { flag: "v3_api", value: false, reason: "disabled" },
        ]} />
    );
    expect(container.textContent).toContain("Feature Flags");
    expect(container.textContent).toContain("u1");
    expect(container.textContent).toContain("2/3 on");
    expect(container.textContent).toContain("dark_mode");
    expect(container.textContent).toContain("rollout");
    expect(container.textContent).toContain("disabled");
  });
});
