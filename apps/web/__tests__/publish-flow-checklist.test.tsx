import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PublishFlowChecklist } from "@/components/publish-flow-checklist";

describe("PublishFlowChecklist", () => {
  it("renders checklist", () => {
    const checks = [
      { key: "manifest", label: "Valid Manifest", passed: true, required: true },
      { key: "security", label: "Security Scan", passed: false, required: true },
    ];
    const { container } = render(
      <PublishFlowChecklist checks={checks} passedCount={1} totalCount={2} pct={50}
        readyToPublish={false} submitLabel="Complete Checks" onSubmit={vi.fn()} />
    );
    expect(container.textContent).toContain("1/2");
    expect(container.textContent).toContain("Valid Manifest");
    expect(container.textContent).toContain("Required");
    expect(container.textContent).toContain("Complete Checks");
  });
  it("ready to publish", () => {
    const fn = vi.fn();
    const checks = [{ key: "m", label: "M", passed: true, required: true }];
    const { container } = render(
      <PublishFlowChecklist checks={checks} passedCount={1} totalCount={1} pct={100}
        readyToPublish={true} submitLabel="Submit for Review" onSubmit={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
