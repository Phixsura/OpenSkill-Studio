import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureToggleList } from "@/components/feature-toggle-list";

describe("FeatureToggleList", () => {
  it("renders toggles", () => {
    const onToggle = vi.fn();
    const { container, getAllByRole } = render(
      <FeatureToggleList onToggle={onToggle} toggles={[
        { key: "new_ui", enabled: true, rolloutPct: 50, segments: ["beta"] },
        { key: "dark_mode", enabled: false, rolloutPct: 0, segments: [] },
      ]} />
    );
    expect(container.textContent).toContain("Feature Toggles");
    expect(container.textContent).toContain("new_ui");
    expect(container.textContent).toContain("50% rollout");
    expect(container.textContent).toContain("beta");
    fireEvent.click(getAllByRole("button")[0]);
    expect(onToggle).toHaveBeenCalledWith("new_ui");
  });
});
