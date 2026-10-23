import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureFlagPanel } from "@/components/feature-flag-panel";

describe("FeatureFlagPanel", () => {
  it("renders flags", () => {
    const onToggle = vi.fn();
    const { container, getAllByRole } = render(
      <FeatureFlagPanel onToggle={onToggle} flags={[
        { key: "new_ui", dflt: true, rolloutPct: 50, targetedUsers: 3, targetedOrgs: 0 },
        { key: "dark_mode", dflt: false, rolloutPct: 0, targetedUsers: 0, targetedOrgs: 0 },
      ]} />
    );
    expect(container.textContent).toContain("Feature Flags");
    expect(container.textContent).toContain("new_ui");
    expect(container.textContent).toContain("50% rollout");
    expect(container.textContent).toContain("3 users");
    fireEvent.click(getAllByRole("button")[0]);
    expect(onToggle).toHaveBeenCalledWith("new_ui");
  });
});
