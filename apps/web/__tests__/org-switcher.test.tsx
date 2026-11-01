import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OrgSwitcher } from "@/components/org-switcher";

describe("OrgSwitcher", () => {
  it("renders orgs", () => {
    const onSwitch = vi.fn();
    const { container, getByText } = render(
      <OrgSwitcher currentName="Acme" canCreate={true} onSwitch={onSwitch} onCreate={vi.fn()}
        orgs={[
          { id: "org1", name: "Acme", role: "admin", plan: "pro", active: true },
          { id: "org2", name: "Side Project", role: "member", plan: "free", active: false },
        ]} />
    );
    expect(container.textContent).toContain("Acme");
    expect(container.textContent).toContain("pro");
    expect(container.textContent).toContain("Side Project");
    expect(container.textContent).toContain("New Organization");
    fireEvent.click(getByText("Side Project"));
    expect(onSwitch).toHaveBeenCalledWith("org2");
  });
});
