import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HotkeyList } from "@/components/hotkey-list";

describe("HotkeyList", () => {
  const shortcuts = [
    { combo: "Ctrl+S", action: "Save", category: "File", enabled: true },
    { combo: "Ctrl+P", action: "Preview", category: "View", enabled: false },
  ];
  it("renders grouped shortcuts", () => {
    const { container } = render(<HotkeyList shortcuts={shortcuts} categories={["File", "View"]} />);
    expect(container.textContent).toContain("Save");
    expect(container.textContent).toContain("Ctrl+S");
    expect(container.textContent).toContain("Preview");
    expect(container.textContent).toContain("File");
    expect(container.textContent).toContain("View");
  });
});
