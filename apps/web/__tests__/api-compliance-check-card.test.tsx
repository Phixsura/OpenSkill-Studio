import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIComplianceCheckCard from "../src/components/api-compliance-check-card";

const rules = [
  { rule_id: "r1", name: "HTTPS Required", category: "security", passed: true },
  { rule_id: "r2", name: "Auth Required", category: "security", passed: true },
  { rule_id: "r3", name: "Docs Complete", category: "documentation", passed: false },
];

describe("APIComplianceCheckCard", () => {
  it("renders score and failing count", () => {
    const { container } = render(<APIComplianceCheckCard rules={rules} score={66.7} appName="App" />);
    expect(container.textContent).toContain("66.7%");
    expect(container.textContent).toContain("1 failing");
  });

  it("shows rules with pass/fail indicators", () => {
    const { container } = render(<APIComplianceCheckCard rules={rules} score={66.7} appName="App" />);
    expect(container.textContent).toContain("HTTPS Required");
    expect(container.textContent).toContain("security");
  });

  it("shows empty state", () => {
    const { container } = render(<APIComplianceCheckCard rules={[]} score={100} appName="App" />);
    expect(container.textContent).toContain("No compliance rules");
  });
});
