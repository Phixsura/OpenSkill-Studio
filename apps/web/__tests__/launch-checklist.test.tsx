import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LaunchChecklist } from "@/components/launch-checklist";

describe("LaunchChecklist", () => {
  it("renders checklist", () => {
    const onLaunch = vi.fn();
    const { container, getByText } = render(
      <LaunchChecklist progressPct={70} readyToLaunch={true} missingRequired={[]}
        onToggle={vi.fn()} onLaunch={onLaunch}
        results={[
          { id: "listing", title: "Complete Listing", category: "listing", required: true, completed: true },
          { id: "docs", title: "API Docs", category: "docs", required: true, completed: true },
          { id: "branding", title: "Branding", category: "branding", required: false, completed: false },
        ]} />
    );
    expect(container.textContent).toContain("Launch Checklist");
    expect(container.textContent).toContain("70%");
    expect(container.textContent).toContain("Complete Listing");
    expect(container.textContent).toContain("Launch App");
    fireEvent.click(getByText("🚀 Launch App"));
    expect(onLaunch).toHaveBeenCalled();
  });
});
