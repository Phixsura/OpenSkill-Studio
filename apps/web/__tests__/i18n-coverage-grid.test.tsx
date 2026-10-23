import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { I18nCoverageGrid } from "@/components/i18n-coverage-grid";

describe("I18nCoverageGrid", () => {
  const locales = [
    { locale: "en", translated: 100, missing: 0, coverage_pct: 100, complete: true },
    { locale: "es", translated: 80, missing: 20, coverage_pct: 80, complete: false },
  ];
  it("renders", () => {
    const { container } = render(
      <I18nCoverageGrid locales={locales} totalKeys={100} fullyTranslated={1} />
    );
    expect(container.textContent).toContain("Translations");
    expect(container.textContent).toContain("1/2 complete");
    expect(container.textContent).toContain("en");
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("es");
    expect(container.textContent).toContain("20 missing");
  });
});
