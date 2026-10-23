import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TenantSettingsForm } from "@/components/tenant-settings-form";

describe("TenantSettingsForm", () => {
  it("renders and saves", () => {
    const onSave = vi.fn();
    const { container, getByText } = render(
      <TenantSettingsForm orgId="org_123" onSave={onSave}
        config={{ theme: "light", locale: "en", timezone: "UTC",
          branding: { accentColor: "#3B82F6", appName: "MyApp" } }} />
    );
    expect(container.textContent).toContain("Organization Settings");
    expect(container.textContent).toContain("org_123");
    fireEvent.click(getByText("Save Settings"));
    expect(onSave).toHaveBeenCalled();
  });
});
