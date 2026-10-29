import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperPortalNavigationCard from "../src/components/api-developer-platform-sdk-api-developer-portal-navigation-card";

const items = [
  { item_id: "home", label: "Home", path: "/", icon: "🏠", children_count: 0 },
  { item_id: "docs", label: "Documentation", path: "/docs", icon: "📚", children_count: 5 },
];

describe("Card", () => {
  it("shows navigation", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperPortalNavigationCard items={items} appName="App" />);
    expect(container.textContent).toContain("Portal Navigation");
    expect(container.textContent).toContain("Home");
    expect(container.textContent).toContain("Documentation");
    expect(container.textContent).toContain("5 children");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperPortalNavigationCard items={[]} appName="App" />);
    expect(container.textContent).toContain("No navigation items");
  });
});
