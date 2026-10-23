import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConsentPreferencesForm } from "@/components/consent-preferences-form";

describe("ConsentPreferencesForm", () => {
  const categories = [
    { id: "essential", label: "Essential", required: true, description: "Required" },
    { id: "analytics", label: "Analytics", required: false, description: "Usage data" },
  ];
  it("renders", () => {
    const { container } = render(<ConsentPreferencesForm categories={categories} onSave={vi.fn()} />);
    expect(container.textContent).toContain("Privacy Preferences");
    expect(container.textContent).toContain("Essential");
    expect(container.textContent).toContain("(Required)");
    expect(container.textContent).toContain("Analytics");
  });
  it("save", () => {
    const fn = vi.fn();
    const { container } = render(<ConsentPreferencesForm categories={categories} onSave={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Save Preferences")!);
    expect(fn).toHaveBeenCalled();
  });
});
