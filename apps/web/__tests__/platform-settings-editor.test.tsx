import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PlatformSettingsEditor } from "@/components/platform-settings-editor";

describe("PlatformSettingsEditor", () => {
  it("renders settings", () => {
    const onSave = vi.fn();
    const { container, getByText } = render(
      <PlatformSettingsEditor onSave={onSave} sections={[
        { section: "general", fields: { platform_name: "OpenSkill", maintenance_mode: false } },
        { section: "security", fields: { mfa_required: false, session_timeout_min: 60 } },
      ]} />
    );
    expect(container.textContent).toContain("Platform Settings");
    expect(container.textContent).toContain("general");
    expect(container.textContent).toContain("OpenSkill");
    expect(container.textContent).toContain("security");
    expect(container.textContent).toContain("60");
    fireEvent.click(getByText("Save"));
    expect(onSave).toHaveBeenCalled();
  });
});
