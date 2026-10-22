import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ManifestTemplatePicker } from "@/components/manifest-template-picker";

describe("ManifestTemplatePicker", () => {
  it("renders all templates", () => {
    const { container } = render(<ManifestTemplatePicker onSelect={vi.fn()} />);
    const buttons = container.querySelectorAll("button");
    expect(buttons.length).toBe(5);
  });

  it("shows template labels", () => {
    const { container } = render(<ManifestTemplatePicker onSelect={vi.fn()} />);
    expect(container.textContent).toContain("Connector");
    expect(container.textContent).toContain("Automation");
    expect(container.textContent).toContain("Analytics");
  });

  it("calls onSelect when clicked", () => {
    const onSelect = vi.fn();
    const { container } = render(<ManifestTemplatePicker onSelect={onSelect} />);
    const buttons = container.querySelectorAll("button");
    fireEvent.click(buttons[0]);
    expect(onSelect).toHaveBeenCalledWith("connector");
  });

  it("highlights selected", () => {
    const { container } = render(<ManifestTemplatePicker onSelect={vi.fn()} selected="automation" />);
    const buttons = container.querySelectorAll("button");
    const automationBtn = Array.from(buttons).find(b => b.textContent?.includes("Automation"));
    expect(automationBtn?.className).toContain("blue");
  });

  it("shows descriptions", () => {
    const { container } = render(<ManifestTemplatePicker onSelect={vi.fn()} />);
    expect(container.textContent).toContain("integrations");
    expect(container.textContent).toContain("workflows");
  });
});
