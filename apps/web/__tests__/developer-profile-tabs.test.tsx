import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeveloperProfileTabs } from "@/components/developer-profile-tabs";

describe("DeveloperProfileTabs", () => {
  it("shows tabs with count", () => {
    const { container } = render(<DeveloperProfileTabs activeTab="apps" onTabChange={vi.fn()} appCount={5} />);
    expect(container.textContent).toContain("Apps (5)");
    expect(container.textContent).toContain("Changelog");
    expect(container.textContent).toContain("About");
  });
  it("highlights active", () => {
    const { container } = render(<DeveloperProfileTabs activeTab="changelog" onTabChange={vi.fn()} appCount={0} />);
    const active = container.querySelector("[class*='border-blue']");
    expect(active?.textContent).toContain("Changelog");
  });
});
