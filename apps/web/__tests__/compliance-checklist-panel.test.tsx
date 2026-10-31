import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ComplianceChecklistPanel } from "@/components/compliance-checklist-panel";

describe("ComplianceChecklistPanel", () => {
  it("renders and toggles", () => {
    const onToggle = vi.fn();
    const { container, getByText } = render(
      <ComplianceChecklistPanel framework="soc2" complianceDisplay="60%" status="in_progress"
        onToggle={onToggle} results={[
          { id: "s1", control: "Access Control", description: "Enforce RBAC", completed: true },
          { id: "s2", control: "Encryption", description: "Encrypt data", completed: false },
        ]} />
    );
    expect(container.textContent).toContain("SOC2 Compliance");
    expect(container.textContent).toContain("60%");
    expect(container.textContent).toContain("in progress");
    fireEvent.click(getByText("Encryption"));
    expect(onToggle).toHaveBeenCalledWith("s2");
  });
});
