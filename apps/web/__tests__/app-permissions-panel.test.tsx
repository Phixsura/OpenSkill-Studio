import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppPermissionsPanel } from "@/components/app-permissions-panel";

const grants = [{ appId: "app1", appName: "My App", scopes: ["read:profile", "read:data"], grantedAt: Date.now() }];

describe("AppPermissionsPanel", () => {
  it("renders grants", () => {
    const { container } = render(<AppPermissionsPanel grants={grants} />);
    expect(container.textContent).toContain("My App");
    expect(container.textContent).toContain("Read your profile");
  });
  it("revoke all", () => {
    const fn = vi.fn();
    const { container } = render(<AppPermissionsPanel grants={grants} onRevoke={fn} />);
    const revokeBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Revoke All");
    if (revokeBtn) fireEvent.click(revokeBtn);
    expect(fn).toHaveBeenCalledWith("app1");
  });
});
