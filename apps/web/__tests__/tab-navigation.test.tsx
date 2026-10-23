import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TabNavigation } from "@/components/tab-navigation";

describe("TabNavigation", () => {
  const tabs = [
    { id: "overview", label: "Overview", icon: "📋" },
    { id: "reviews", label: "Reviews", icon: "⭐" },
    { id: "docs", label: "Docs", icon: "📚" },
  ];
  it("renders", () => {
    const { container } = render(
      <TabNavigation tabs={tabs} activeTab="overview" onTabChange={vi.fn()} />
    );
    expect(container.textContent).toContain("📋");
    expect(container.textContent).toContain("Overview");
    expect(container.textContent).toContain("Reviews");
    expect(container.textContent).toContain("Docs");
  });
  it("tab change", () => {
    const fn = vi.fn();
    const { container } = render(
      <TabNavigation tabs={tabs} activeTab="overview" onTabChange={fn} />
    );
    fireEvent.click(container.querySelectorAll("button")[1]);
    expect(fn).toHaveBeenCalledWith("reviews");
  });
});
