import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ComplianceDashboard } from "@/components/compliance-dashboard";

const mockRecords = [
  { developerId: "d1", developerName: "Alice", status: "compliant" as const,
    violations: 0, warnings: 0, hasAcceptedTos: true },
  { developerId: "d2", developerName: "Bob", status: "violation" as const,
    violations: 2, warnings: 1, hasAcceptedTos: true },
  { developerId: "d3", developerName: "Charlie", status: "suspended" as const,
    violations: 3, warnings: 2, hasAcceptedTos: false },
];

describe("ComplianceDashboard", () => {
  it("renders status summary", () => {
    const { container } = render(<ComplianceDashboard records={mockRecords} />);
    expect(container.textContent).toContain("Developer Compliance");
    expect(container.textContent).toContain("Compliant");
    expect(container.textContent).toContain("Suspended");
  });

  it("shows violations and warnings", () => {
    const { container } = render(<ComplianceDashboard records={mockRecords} />);
    expect(container.textContent).toContain("2 violations");
    expect(container.textContent).toContain("ToS pending");
  });

  it("calls onSuspend", () => {
    const onSuspend = vi.fn();
    const { getByText } = render(<ComplianceDashboard records={mockRecords} onSuspend={onSuspend} />);
    fireEvent.click(getByText("Suspend"));
    expect(onSuspend).toHaveBeenCalledWith("d2");
  });

  it("calls onRestore", () => {
    const onRestore = vi.fn();
    const { getByText } = render(<ComplianceDashboard records={mockRecords} onRestore={onRestore} />);
    fireEvent.click(getByText("Restore"));
    expect(onRestore).toHaveBeenCalledWith("d3");
  });
});
