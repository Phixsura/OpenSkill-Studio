import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperSettingsLayout } from "@/components/developer-settings-layout";

describe("DeveloperSettingsLayout", () => {
  const tabs = [
    { key: "profile", title: "Profile", icon: "👤" },
    { key: "security", title: "Security", icon: "🔒" },
    { key: "danger", title: "Danger Zone", icon: "⚠️" },
  ];
  it("renders", () => {
    const { container } = render(
      <DeveloperSettingsLayout tabs={tabs}><p>Settings content</p></DeveloperSettingsLayout>
    );
    expect(container.textContent).toContain("Settings");
    expect(container.textContent).toContain("Profile");
    expect(container.textContent).toContain("Danger Zone");
    expect(container.textContent).toContain("Settings content");
  });
  it("switches tab", () => {
    const { container } = render(
      <DeveloperSettingsLayout tabs={tabs}><p>C</p></DeveloperSettingsLayout>
    );
    fireEvent.click(container.querySelectorAll("button")[1]);
    expect(container.querySelectorAll("button")[1].className).toContain("blue");
  });
});
