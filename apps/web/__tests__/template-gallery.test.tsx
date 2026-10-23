import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TemplateGallery } from "@/components/template-gallery";

describe("TemplateGallery", () => {
  const templates = [
    { id: "basic", name: "Basic App", icon: "📦", description: "Minimal scaffold",
      tech: ["TypeScript"], files: 5, category: "starter" },
    { id: "react", name: "React Widget", icon: "⚛️", description: "Embeddable component",
      tech: ["React", "TypeScript"], files: 12, category: "frontend" },
  ];
  it("renders", () => {
    const { container } = render(<TemplateGallery templates={templates} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("Start with a Template");
    expect(container.textContent).toContain("Basic App");
    expect(container.textContent).toContain("📦");
    expect(container.textContent).toContain("React Widget");
    expect(container.textContent).toContain("TypeScript");
  });
  it("select", () => {
    const fn = vi.fn();
    const { container } = render(<TemplateGallery templates={templates} onSelect={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("basic");
  });
});
