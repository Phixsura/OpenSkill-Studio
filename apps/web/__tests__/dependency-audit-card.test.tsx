import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DependencyAuditCard } from "@/components/dependency-audit-card";

describe("DependencyAuditCard", () => {
  it("renders audit", () => {
    const { container } = render(<DependencyAuditCard total={20} vulnCount={2} outdatedCount={5} score={70} grade="B" />);
    expect(container.textContent).toContain("20");
    expect(container.textContent).toContain("2");
    expect(container.textContent).toContain("B");
  });
  it("clean audit", () => {
    const { container } = render(<DependencyAuditCard total={10} vulnCount={0} outdatedCount={0} score={100} grade="A" />);
    expect(container.textContent).toContain("A");
  });
});
