import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CommandPaletteModal } from "@/components/command-palette-modal";

describe("CommandPaletteModal", () => {
  it("renders palette", () => {
    const { container } = render(
      <CommandPaletteModal onSelect={vi.fn()} onClose={vi.fn()} commands={[
        { id: "deploy", label: "Deploy App", shortcut: "⌘D", category: "ops" },
        { id: "settings", label: "Open Settings", shortcut: "⌘,", category: "nav" },
      ]} />
    );
    expect(container.textContent).toContain("Deploy App");
    expect(container.textContent).toContain("⌘D");
    expect(container.textContent).toContain("Open Settings");
    expect(container.textContent).toContain("nav");
  });
});
