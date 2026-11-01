import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { HomeDashboardView } from "@/components/home-dashboard-view";

describe("HomeDashboardView", () => {
  it("renders dashboard", () => {
    const onAction = vi.fn();
    const { container, getByText } = render(
      <HomeDashboardView greeting="Welcome, Alice!" plan="pro"
        stats={[{ icon: "📱", label: "Apps", value: "5" }]}
        topApps={[{ name: "TopApp", installs: 5000 }]}
        quickActions={["Create App", "Docs"]}
        onAction={onAction} />
    );
    expect(container.textContent).toContain("Welcome, Alice!");
    expect(container.textContent).toContain("pro");
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("TopApp");
    expect(container.textContent).toContain("5,000 installs");
    fireEvent.click(getByText("Docs"));
    expect(onAction).toHaveBeenCalledWith("Docs");
  });
});
