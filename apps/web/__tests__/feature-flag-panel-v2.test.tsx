import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FeatureFlagPanelV2 } from "@/components/feature-flag-panel-v2";

describe("FeatureFlagPanelV2", () => {
  it("renders flags", () => {
    const flags = [
      { id: "new_search", description: "New search", enabled: true, rollout_pct: 100 },
      { id: "ai_recs", description: "AI recommendations", enabled: true, rollout_pct: 50 },
      { id: "dark_v2", description: "Dark mode v2", enabled: false, rollout_pct: 0 },
    ];
    const { container } = render(<FeatureFlagPanelV2 flags={flags} />);
    expect(container.textContent).toContain("new_search");
    expect(container.textContent).toContain("2/3 enabled");
    expect(container.textContent).toContain("50%");
  });
});
