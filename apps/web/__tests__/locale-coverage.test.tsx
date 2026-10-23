import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LocaleCoverage } from "@/components/locale-coverage";

describe("LocaleCoverage", () => {
  const locales = [
    { locale: "es", coveragePct: 100, complete: true, missingCount: 0 },
    { locale: "fr", coveragePct: 66.7, complete: false, missingCount: 1 },
  ];
  it("renders coverage", () => {
    const { container } = render(<LocaleCoverage locales={locales} baseKeys={3} />);
    expect(container.textContent).toContain("es");
    expect(container.textContent).toContain("Complete");
    expect(container.textContent).toContain("fr");
    expect(container.textContent).toContain("1 missing");
    expect(container.textContent).toContain("3 base keys");
  });
});
