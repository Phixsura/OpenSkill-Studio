import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppPreviewHover } from "@/components/app-preview-hover";

describe("AppPreviewHover", () => {
  it("shows when visible", () => {
    const { container } = render(<AppPreviewHover name="App" description="Desc" category="connector" installs={42} health={95} visible={true} />);
    expect(container.textContent).toContain("App");
  });
  it("hidden when not visible", () => {
    const { container } = render(<AppPreviewHover name="X" description="" category="" installs={0} health={0} visible={false} />);
    expect(container.innerHTML).toBe("");
  });
});
