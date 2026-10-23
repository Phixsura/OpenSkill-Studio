import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TranslationProgressCard } from "@/components/translation-progress-card";

describe("TranslationProgressCard", () => {
  it("renders locales", () => {
    const locales = [
      { locale: "zh", completeness_pct: 80, missing_count: 5 },
      { locale: "ja", completeness_pct: 100, missing_count: 0 },
    ];
    const { container } = render(<TranslationProgressCard locales={locales} baseLocale="en" />);
    expect(container.textContent).toContain("zh");
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("5 missing");
    expect(container.textContent).toContain("✅");
  });
});
