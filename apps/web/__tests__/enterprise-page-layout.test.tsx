import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EnterprisePageLayout } from "@/components/enterprise-page-layout";

describe("EnterprisePageLayout", () => {
  it("renders", () => {
    const features = [{ title: "Unlimited", description: "No limits", icon: "♾️" }];
    const cases = [{ company: "Acme", industry: "FinTech", quote: "Amazing!", results: "10K users" }];
    const { container } = render(
      <EnterprisePageLayout features={features} caseStudies={cases} onContactSales={vi.fn()} />
    );
    expect(container.textContent).toContain("OpenSkill for Enterprise");
    expect(container.textContent).toContain("Unlimited");
    expect(container.textContent).toContain("Acme");
    expect(container.textContent).toContain("Amazing!");
    expect(container.textContent).toContain("Contact Sales");
  });
  it("contact sales", () => {
    const fn = vi.fn();
    const { container } = render(
      <EnterprisePageLayout features={[]} caseStudies={[]} onContactSales={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Contact Sales")!);
    expect(fn).toHaveBeenCalled();
  });
});
