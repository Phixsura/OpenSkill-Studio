import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PlatformHeader } from "@/components/platform-header";

describe("PlatformHeader", () => {
  it("renders header", () => {
    const onNav = vi.fn();
    const { container, getByText } = render(
      <PlatformHeader user={{ name: "Alice Chen", initials: "AC", avatarUrl: "" }}
        orgName="Acme" unreadCount={5} planBadge="PRO"
        navLinks={[{ label: "Dashboard", path: "/dashboard" }, { label: "Apps", path: "/apps" }]}
        onNavigate={onNav} />
    );
    expect(container.textContent).toContain("OpenSkill");
    expect(container.textContent).toContain("Alice Chen");
    expect(container.textContent).toContain("AC");
    expect(container.textContent).toContain("PRO");
    expect(container.textContent).toContain("5");
    fireEvent.click(getByText("Dashboard"));
    expect(onNav).toHaveBeenCalledWith("/dashboard");
  });
});
