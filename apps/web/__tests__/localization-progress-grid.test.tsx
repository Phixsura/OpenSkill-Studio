import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LocalizationProgressGrid } from "@/components/localization-progress-grid";

describe("LocalizationProgressGrid", () => {
  const locales = [
    { locale: "en", language: "English", completed_fields: 4, total_fields: 4, progress: 100, is_default: true },
    { locale: "es", language: "Spanish", completed_fields: 1, total_fields: 4, progress: 25, is_default: false },
    { locale: "fr", language: "French", completed_fields: 0, total_fields: 4, progress: 0, is_default: false },
  ];
  it("renders grid", () => {
    const { container } = render(<LocalizationProgressGrid locales={locales} overallProgress={42} />);
    expect(container.textContent).toContain("Localization");
    expect(container.textContent).toContain("Overall: 42%");
    expect(container.textContent).toContain("English");
    expect(container.textContent).toContain("4/4 fields");
    expect(container.textContent).toContain("1/4 fields");
  });
});
