import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RollbackProgressView } from "@/components/rollback-progress-view";

describe("RollbackProgressView", () => {
  const steps = [
    { name: "stop_traffic", status: "completed" },
    { name: "swap_version", status: "in_progress" },
    { name: "health_check", status: "pending" },
    { name: "resume_traffic", status: "pending" },
  ];
  it("renders", () => {
    const { container } = render(
      <RollbackProgressView rollbackId="rb_1" fromVersion="2.1.0" toVersion="2.0.5"
        reason="Error spike" steps={steps} status="pending" onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("Rolling Back");
    expect(container.textContent).toContain("v2.1.0 → v2.0.5");
    expect(container.textContent).toContain("Error spike");
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("⏳");
  });
  it("cancel", () => {
    const fn = vi.fn();
    const { container } = render(
      <RollbackProgressView rollbackId="rb_1" fromVersion="2.1.0" toVersion="2.0.5"
        reason="x" steps={steps} status="pending" onCancel={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Cancel Rollback")!);
    expect(fn).toHaveBeenCalled();
  });
});
