import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TestSuiteStatusBadge } from "@/components/test-suite-status-badge";

describe("TestSuiteStatusBadge", () => {
  it("green badge", () => {
    const { container } = render(<TestSuiteStatusBadge suite="Unit Tests" passRate={100} status="green" passed={50} total={50} />);
    expect(container.textContent).toContain("Unit Tests");
    expect(container.textContent).toContain("50/50");
    expect(container.textContent).toContain("✅");
  });
  it("red badge", () => {
    const { container } = render(<TestSuiteStatusBadge suite="E2E" passRate={80} status="red" passed={8} total={10} />);
    expect(container.textContent).toContain("❌");
    expect(container.textContent).toContain("80%");
  });
});
