import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SandboxTemplatePicker } from "@/components/sandbox-template-picker";

const templates = [
  { templateId: "py", name: "Python Basic", runtime: "python", description: "Basic Python", category: "starter" },
  { templateId: "node", name: "Node API", runtime: "node", description: "Node.js API", category: "api" },
];

describe("SandboxTemplatePicker", () => {
  it("renders templates", () => {
    const { container } = render(<SandboxTemplatePicker templates={templates} />);
    expect(container.textContent).toContain("Python Basic");
    expect(container.textContent).toContain("Node API");
  });
  it("selects template", () => {
    const fn = vi.fn();
    const { container } = render(<SandboxTemplatePicker templates={templates} onSelect={fn} />);
    const cards = container.querySelectorAll(".grid button");
    fireEvent.click(cards[0]);
    expect(fn).toHaveBeenCalledWith("py");
  });
});
