import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TemplateGalleryGrid } from "@/components/template-gallery-grid";

describe("TemplateGalleryGrid", () => {
  const templates = [
    { id: "t1", name: "Connector", category: "connector", description: "Simple connector", difficulty: "beginner", stars: 100 },
    { id: "t2", name: "Bot", category: "communication", description: "Chat bot", difficulty: "advanced", stars: 50 },
  ];
  it("renders grid", () => {
    const { container } = render(<TemplateGalleryGrid templates={templates} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("Connector");
    expect(container.textContent).toContain("Bot");
    expect(container.textContent).toContain("⭐ 100");
  });
  it("calls onSelect", () => {
    const fn = vi.fn();
    const { container } = render(<TemplateGalleryGrid templates={templates} onSelect={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("t1");
  });
  it("empty state", () => {
    const { container } = render(<TemplateGalleryGrid templates={[]} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("No templates");
  });
});
