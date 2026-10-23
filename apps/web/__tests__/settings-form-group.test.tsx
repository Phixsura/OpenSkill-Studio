import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SettingsFormGroup } from "@/components/settings-form-group";

describe("SettingsFormGroup", () => {
  it("renders settings", () => {
    const settings = [
      { key: "app_name", type: "string", label: "App Name", required: true },
      { key: "https", type: "boolean", label: "Require HTTPS", default: true },
    ];
    const { container } = render(
      <SettingsFormGroup group="General" icon="⚙️" settings={settings} values={{ app_name: "MyApp" }} onChange={vi.fn()} />
    );
    expect(container.textContent).toContain("General");
    expect(container.textContent).toContain("App Name");
    expect(container.textContent).toContain("*");
    expect(container.querySelector("input[type='checkbox']")).toBeTruthy();
  });
});
