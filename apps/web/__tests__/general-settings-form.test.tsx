import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GeneralSettingsForm } from "@/components/general-settings-form";

describe("GeneralSettingsForm", () => {
  const fields = [
    { key: "name", label: "App Name", type: "text", value: "SuperApp", required: true },
    { key: "category", label: "Category", type: "select", value: "tools", options: ["tools", "other"] },
  ];
  it("renders form", () => {
    const { container } = render(
      <GeneralSettingsForm fields={fields} currentVersion="2.0.0" errors={[]} onSave={vi.fn()} />
    );
    expect(container.textContent).toContain("General Settings");
    expect(container.textContent).toContain("App Name");
    expect(container.textContent).toContain("Category");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("Save Settings");
  });
  it("shows errors", () => {
    const { container } = render(
      <GeneralSettingsForm fields={fields} currentVersion="1.0" errors={["Name required"]} onSave={vi.fn()} />
    );
    expect(container.textContent).toContain("Name required");
  });
});
