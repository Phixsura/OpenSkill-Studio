import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CommandPaletteUI } from "@/components/command-palette-ui";

const mockCommands = [
  { commandId: "format", title: "Format Document", category: "editor", shortcut: "Ctrl+Shift+F" },
  { commandId: "open_file", title: "Open File", category: "file", description: "Open a file" },
  { commandId: "build", title: "Build Project", category: "project" },
];
const mockRecent = [
  { commandId: "format", title: "Format Document", category: "editor" },
];

describe("CommandPaletteUI", () => {
  it("renders search input", () => {
    const { container } = render(
      <CommandPaletteUI commands={mockCommands} recentCommands={mockRecent} categories={["editor", "file", "project"]} />
    );
    expect(container.querySelector("input")).toBeDefined();
    expect(container.textContent).toContain("Format Document");
  });

  it("shows recent commands", () => {
    const { container } = render(
      <CommandPaletteUI commands={mockCommands} recentCommands={mockRecent} categories={[]} />
    );
    expect(container.textContent).toContain("Recent");
  });

  it("calls onExecute", () => {
    const onExecute = vi.fn();
    const { getByText } = render(
      <CommandPaletteUI commands={mockCommands} recentCommands={[]} categories={[]} onExecute={onExecute} />
    );
    fireEvent.click(getByText("Build Project"));
    expect(onExecute).toHaveBeenCalledWith("build");
  });

  it("shows keyboard shortcuts", () => {
    const { container } = render(
      <CommandPaletteUI commands={mockCommands} recentCommands={[]} categories={[]} />
    );
    expect(container.textContent).toContain("Ctrl+Shift+F");
  });
});
