import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConsentBanner } from "@/components/consent-banner";

describe("ConsentBanner", () => {
  const items = [
    { type: "essential", description: "Required", required: true, granted: true, editable: false },
    { type: "analytics", description: "Usage data", required: false, granted: false, editable: true },
  ];
  it("renders consent options", () => {
    const { container } = render(<ConsentBanner items={items} onAcceptAll={vi.fn()} onSave={vi.fn()} />);
    expect(container.textContent).toContain("Cookie");
    expect(container.textContent).toContain("essential");
    expect(container.textContent).toContain("analytics");
    expect(container.textContent).toContain("Accept All");
  });
  it("accept all", () => {
    const fn = vi.fn();
    const { container } = render(<ConsentBanner items={items} onAcceptAll={fn} onSave={vi.fn()} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Accept All")!);
    expect(fn).toHaveBeenCalled();
  });
});
