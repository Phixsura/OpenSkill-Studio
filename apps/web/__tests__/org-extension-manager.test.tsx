import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OrgExtensionManager } from "@/components/org-extension-manager";

const mockExts = [
  { id: "e1", name: "Slack Bot", icon: "💬", version: "2.1.0", status: "enabled" as const, installedAt: "Oct 1", lastUsed: "2m ago", usagePercent: 85 },
  { id: "e2", name: "Analytics", icon: "📊", version: "1.0.0", status: "disabled" as const, installedAt: "Sep 1", lastUsed: "30d ago", usagePercent: 5 },
  { id: "e3", name: "Broken Ext", icon: "💥", version: "0.9.0", status: "error" as const, installedAt: "Oct 10", lastUsed: "1d ago", usagePercent: 0 },
];

describe("OrgExtensionManager", () => {
  it("renders extensions", () => {
    const { container } = render(<OrgExtensionManager extensions={mockExts} orgName="Acme" />);
    expect(container.textContent).toContain("Acme Extensions");
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("3 extensions");
  });

  it("filters by status", () => {
    const { container, getByText } = render(<OrgExtensionManager extensions={mockExts} orgName="Acme" />);
    fireEvent.click(getByText("disabled"));
    expect(container.textContent).toContain("1 extension");
    expect(container.textContent).toContain("Analytics");
  });

  it("shows enable/disable buttons by status", () => {
    const onDisable = vi.fn();
    const onEnable = vi.fn();
    const { getByText } = render(
      <OrgExtensionManager extensions={mockExts} orgName="Acme" onDisable={onDisable} onEnable={onEnable} />
    );
    fireEvent.click(getByText("Disable"));
    expect(onDisable).toHaveBeenCalledWith("e1");
    fireEvent.click(getByText("Enable"));
    expect(onEnable).toHaveBeenCalledWith("e2");
  });
});
