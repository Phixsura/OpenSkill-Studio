import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OrgSettingsPage } from "@/components/org-settings-page";

describe("OrgSettingsPage", () => {
  const groups = [{
    id: "general", label: "General", icon: "⚙️",
    settings: [{ key: "org_name", label: "Name", type: "text", value: "Acme" }],
  }];
  it("renders settings", () => {
    const { container } = render(<OrgSettingsPage groups={groups} orgName="Acme Corp" onSave={vi.fn()} />);
    expect(container.textContent).toContain("Acme Corp Settings");
    expect(container.textContent).toContain("General");
    expect(container.textContent).toContain("Name");
    expect(container.textContent).toContain("Save Settings");
  });
});
