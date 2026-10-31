import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppSettingsLayout } from "@/components/app-settings-layout";

describe("AppSettingsLayout", () => {
  it("renders settings", () => {
    const onSelect = vi.fn();
    const { container, getByText } = render(
      <AppSettingsLayout appName="My App" activeSection="general" onSelectSection={onSelect}
        sections={[
          { id: "general", title: "General", icon: "⚙️", fields: [] },
          { id: "danger", title: "Danger Zone", icon: "⚠️", fields: [] },
        ]}>
        <p>Settings content</p>
      </AppSettingsLayout>
    );
    expect(container.textContent).toContain("My App Settings");
    expect(container.textContent).toContain("General");
    expect(container.textContent).toContain("Danger Zone");
    expect(container.textContent).toContain("Settings content");
    fireEvent.click(getByText("⚠️ Danger Zone"));
    expect(onSelect).toHaveBeenCalledWith("danger");
  });
});
