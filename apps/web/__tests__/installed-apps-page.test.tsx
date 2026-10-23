import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { InstalledAppsPage } from "@/components/installed-apps-page";

describe("InstalledAppsPage", () => {
  const apps = [
    { id: "a1", name: "SuperApp", icon: "🚀", version: "2.0.0", installedAt: "2026-01-01",
      apiCalls30d: 5000, status: "active", hasUpdate: true, updateVersion: "2.1.0" },
  ];
  it("renders installed apps", () => {
    const { container } = render(
      <InstalledAppsPage apps={apps} totalApiCalls={5000} updatesAvailable={1}
        onUninstall={vi.fn()} onUpdate={vi.fn()} onOpen={vi.fn()} />
    );
    expect(container.textContent).toContain("My Apps");
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("Update: v2.1.0");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("1 updates");
  });
});
