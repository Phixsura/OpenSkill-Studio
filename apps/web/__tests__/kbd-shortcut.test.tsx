import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { KbdShortcut } from "@/components/kbd-shortcut";

describe("KbdShortcut", () => {
  it("renders mac shortcut", () => {
    const { container } = render(
      <KbdShortcut formattedKeys={["⌘", "K"]} display="⌘K" label="Search" />
    );
    expect(container.textContent).toContain("Search");
    expect(container.textContent).toContain("⌘");
    expect(container.textContent).toContain("K");
    expect(container.querySelector("kbd")).toBeTruthy();
  });
  it("renders without label", () => {
    const { container } = render(
      <KbdShortcut formattedKeys={["Ctrl", "S"]} display="Ctrl+S" />
    );
    expect(container.textContent).toContain("Ctrl");
    expect(container.textContent).toContain("S");
  });
});
