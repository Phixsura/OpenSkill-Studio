import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PortalHomePage } from "@/components/portal-home-page";

describe("PortalHomePage", () => {
  const quickLinks = [{ label: "Create App", href: "/new", icon: "➕" }];
  const deploys = [{ app: "MyApp", version: "2.0.0", status: "success" }];
  it("renders portal home", () => {
    const { container } = render(
      <PortalHomePage greeting="Good morning, Alice!" stats={{ apps: 5, installs: 12000, notifications: 3 }}
        quickLinks={quickLinks} recentDeploys={deploys}
        announcements={[{ title: "SDK v3!", type: "feature" }]} onNavigate={vi.fn()} />
    );
    expect(container.textContent).toContain("Good morning, Alice!");
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("12,000");
    expect(container.textContent).toContain("Create App");
    expect(container.textContent).toContain("MyApp v2.0.0");
    expect(container.textContent).toContain("SDK v3!");
  });
});
