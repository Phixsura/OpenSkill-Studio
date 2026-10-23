import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppDetailTabBar } from "@/components/app-detail-tab-bar";

describe("AppDetailTabBar", () => {
  const tabs = [{ key: "overview", title: "Overview" }, { key: "reviews", title: "Reviews (50)" }];
  it("renders tabs", () => {
    const { container } = render(<AppDetailTabBar tabs={tabs} activeTab="overview" onTabChange={vi.fn()} />);
    expect(container.textContent).toContain("Overview");
    expect(container.textContent).toContain("Reviews (50)");
  });
  it("switches tab", () => {
    const fn = vi.fn();
    const { container } = render(<AppDetailTabBar tabs={tabs} activeTab="overview" onTabChange={fn} />);
    fireEvent.click(container.querySelectorAll("button")[1]);
    expect(fn).toHaveBeenCalledWith("reviews");
  });
});
