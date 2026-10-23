import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LandingPageEditor } from "@/components/landing-page-editor";

describe("LandingPageEditor", () => {
  it("renders", () => {
    const sections = [{ type: "hero", order: 0 }, { type: "features", order: 1 }];
    const { container } = render(
      <LandingPageEditor appName="MyApp" sections={sections} availableTypes={["hero", "cta"]}
        onAddSection={vi.fn()} onRemoveSection={vi.fn()} onPreview={vi.fn()} />
    );
    expect(container.textContent).toContain("MyApp Landing Page");
    expect(container.textContent).toContain("hero");
    expect(container.textContent).toContain("features");
  });
  it("empty state", () => {
    const { container } = render(
      <LandingPageEditor appName="X" sections={[]} availableTypes={[]}
        onAddSection={vi.fn()} onRemoveSection={vi.fn()} onPreview={vi.fn()} />
    );
    expect(container.textContent).toContain("No sections yet");
  });
  it("remove", () => {
    const fn = vi.fn();
    const { container } = render(
      <LandingPageEditor appName="X" sections={[{ type: "hero", order: 0 }]} availableTypes={[]}
        onAddSection={vi.fn()} onRemoveSection={fn} onPreview={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Remove")!);
    expect(fn).toHaveBeenCalledWith(0);
  });
});
