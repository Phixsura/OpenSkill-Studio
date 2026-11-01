import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WorkspaceSettingsPanel } from "@/components/workspace-settings-panel";

describe("WorkspaceSettingsPanel", () => {
  it("renders settings", () => {
    const { container } = render(
      <WorkspaceSettingsPanel customized={2} total={5} onUpdate={vi.fn()} onReset={vi.fn()}
        settings={{ theme: "dark", language: "en", timezone: "UTC" }} />
    );
    expect(container.textContent).toContain("Workspace Settings");
    expect(container.textContent).toContain("2/5 customized");
    expect(container.textContent).toContain("theme");
    expect(container.textContent).toContain("dark");
    expect(container.textContent).toContain("timezone");
    expect(container.textContent).toContain("Reset");
  });
});
