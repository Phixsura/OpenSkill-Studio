import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LegalPageLayout } from "@/components/legal-page-layout";

describe("LegalPageLayout", () => {
  const sections = ["Introduction", "Account Terms", "API Usage"];
  it("renders", () => {
    const { container } = render(
      <LegalPageLayout title="Terms of Service" lastUpdated="2026-10-01"
        sections={sections} activeSection={null} onSectionClick={vi.fn()}>
        <p>Legal content here</p>
      </LegalPageLayout>
    );
    expect(container.textContent).toContain("Terms of Service");
    expect(container.textContent).toContain("2026-10-01");
    expect(container.textContent).toContain("Introduction");
    expect(container.textContent).toContain("Legal content here");
  });
  it("section click", () => {
    const fn = vi.fn();
    const { container } = render(
      <LegalPageLayout title="T" lastUpdated="" sections={sections}
        activeSection={null} onSectionClick={fn}>
        <p>C</p>
      </LegalPageLayout>
    );
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("Introduction");
  });
});
