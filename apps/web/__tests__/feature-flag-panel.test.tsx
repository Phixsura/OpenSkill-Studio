import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureFlagPanel } from "@/components/feature-flag-panel";

describe("FeatureFlagPanel", () => {
  it("renders flags", () => {
    const { container } = render(
      <FeatureFlagPanel environment="production" enabled={1} total={2} onToggle={vi.fn()}
        flags={[
          { key: "dark_mode", label: "Dark Mode", enabled: true, rolloutPct: 100, environments: ["production"] },
          { key: "beta_ai", label: "Beta AI", enabled: false, rolloutPct: 50, environments: ["staging"] },
        ]} />
    );
    expect(container.textContent).toContain("Feature Flags");
    expect(container.textContent).toContain("production");
    expect(container.textContent).toContain("1/2 on");
    expect(container.textContent).toContain("Dark Mode");
    expect(container.textContent).toContain("50% rollout");
  });
});
