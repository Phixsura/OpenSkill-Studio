import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GlobalNav } from "@/components/global-nav";

describe("GlobalNav", () => {
  const nav = [{ id: "marketplace", label: "Marketplace", href: "/marketplace", icon: "🏪", active: true }];
  const user = { name: "Alice", initials: "AC", plan: "pro", menu: [{ label: "Profile", href: "/profile", icon: "👤" }] };
  it("renders logged in", () => {
    const { container } = render(
      <GlobalNav nav={nav} user={user} loggedIn={true} notifications={5} onNavigate={vi.fn()} onSearch={vi.fn()} />
    );
    expect(container.textContent).toContain("OpenSkill");
    expect(container.textContent).toContain("Marketplace");
    expect(container.textContent).toContain("AC");
    expect(container.textContent).toContain("5");
  });
  it("renders logged out", () => {
    const { container } = render(
      <GlobalNav nav={nav} user={null} loggedIn={false} notifications={0} onNavigate={vi.fn()} onSearch={vi.fn()} />
    );
    expect(container.textContent).toContain("Sign In");
  });
});
