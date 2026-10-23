import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OrgSwitcher } from "@/components/org-switcher";

describe("OrgSwitcher", () => {
  const orgs = [
    { id: "o1", name: "Acme Corp", initials: "AC", role: "owner", plan: "pro", isCurrent: true },
    { id: "o2", name: "Side Project", initials: "SP", role: "admin", plan: "free", isCurrent: false },
  ];
  it("renders orgs", () => {
    const { container } = render(
      <OrgSwitcher orgs={orgs} current={orgs[0]} canCreate={true} onSwitch={vi.fn()} onCreate={vi.fn()} />
    );
    expect(container.textContent).toContain("Acme Corp");
    expect(container.textContent).toContain("Side Project");
    expect(container.textContent).toContain("Create Organization");
  });
  it("switch org", () => {
    const fn = vi.fn();
    const { container } = render(
      <OrgSwitcher orgs={orgs} current={orgs[0]} canCreate={true} onSwitch={fn} onCreate={vi.fn()} />
    );
    const switchBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Side Project"))!;
    fireEvent.click(switchBtn);
    expect(fn).toHaveBeenCalledWith("o2");
  });
});
