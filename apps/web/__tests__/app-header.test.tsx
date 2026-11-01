import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppHeader } from "@/components/app-header";

describe("AppHeader", () => {
  const nav = [{ label: "Marketplace", href: "/marketplace", icon: "🏪" }];
  it("renders logged in", () => {
    const { container } = render(
      <AppHeader nav={nav} user={{ name: "Alice", initials: "AC", avatar: null }}
        notifications={3} loggedIn={true} onNavigate={vi.fn()} />
    );
    expect(container.textContent).toContain("OpenSkill");
    expect(container.textContent).toContain("Marketplace");
    expect(container.textContent).toContain("AC");
    expect(container.textContent).toContain("3");
  });
  it("renders logged out", () => {
    const { container } = render(
      <AppHeader nav={nav} user={null} notifications={0} loggedIn={false} onNavigate={vi.fn()} />
    );
    expect(container.textContent).toContain("Sign In");
  });
});
