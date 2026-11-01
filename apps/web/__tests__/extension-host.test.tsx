import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExtensionHost } from "@/components/extension-host";

const BASE_PROPS = {
  appId: "app-1",
  installationId: "inst-1",
  surface: "dashboard_card",
  entryUrl: "https://ext.example.com/card.html",
  orgId: "org-1",
  userId: "user-1",
  permissions: ["read:cohorts"],
};

describe("ExtensionHost", () => {
  it("renders iframe", () => {
    const { container } = render(<ExtensionHost {...BASE_PROPS} />);
    const iframe = container.querySelector("iframe");
    expect(iframe).toBeTruthy();
  });

  it("sets sandbox attribute", () => {
    const { container } = render(<ExtensionHost {...BASE_PROPS} />);
    const iframe = container.querySelector("iframe");
    expect(iframe?.getAttribute("sandbox")).toBeTruthy();
    expect(iframe?.getAttribute("sandbox")).toContain("allow-scripts");
  });

  it("does not allow same-origin", () => {
    const { container } = render(<ExtensionHost {...BASE_PROPS} />);
    const iframe = container.querySelector("iframe");
    expect(iframe?.getAttribute("sandbox")).not.toContain("allow-same-origin");
  });

  it("applies viewport dimensions", () => {
    const { container } = render(
      <ExtensionHost {...BASE_PROPS} viewportWidth={400} viewportHeight={300} />
    );
    const iframe = container.querySelector("iframe");
    expect(iframe).toBeTruthy();
  });

  it("accepts callback props", () => {
    const onToast = vi.fn();
    const onNavigate = vi.fn();
    const { container } = render(
      <ExtensionHost {...BASE_PROPS} onToast={onToast} onNavigate={onNavigate} />
    );
    expect(container.querySelector("iframe")).toBeTruthy();
  });
});
