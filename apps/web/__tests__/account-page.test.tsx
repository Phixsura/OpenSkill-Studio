import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AccountPage } from "@/components/account-page";

describe("AccountPage", () => {
  it("renders account", () => {
    const { container } = render(
      <AccountPage
        profile={{ name: "Alice", email: "a@b.com", avatarUrl: "https://img.com/a.png", bio: "Builder", timezone: "UTC" }}
        security={{ twoFactorEnabled: true, activeSessions: 2, passwordUpdated: "2026-01-01" }}
        connectedAccounts={[{ provider: "GitHub", connected: true, username: "alice" }]}
        sections={["profile"]}
        onEditProfile={vi.fn()} onEnable2FA={vi.fn()} onConnect={vi.fn()} />
    );
    expect(container.textContent).toContain("Account Settings");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("Enabled");
    expect(container.textContent).toContain("GitHub");
    expect(container.textContent).toContain("alice");
  });
});
