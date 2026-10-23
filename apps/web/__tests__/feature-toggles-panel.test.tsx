import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureTogglesPanel } from "@/components/feature-toggles-panel";

describe("FeatureTogglesPanel", () => {
  const toggles = { dark_mode: true, beta_ui: false };
  it("renders toggles", () => {
    const { container } = render(
      <FeatureTogglesPanel toggles={toggles} total={2} enabled={1} onToggle={vi.fn()} />
    );
    expect(container.textContent).toContain("dark_mode");
    expect(container.textContent).toContain("beta_ui");
    expect(container.textContent).toContain("1/2");
  });
  it("toggle click", () => {
    const fn = vi.fn();
    const { container } = render(
      <FeatureTogglesPanel toggles={toggles} total={2} enabled={1} onToggle={fn} />
    );
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("dark_mode");
  });
});
