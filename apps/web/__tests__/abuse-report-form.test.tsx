import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AbuseReportForm } from "@/components/abuse-report-form";

describe("AbuseReportForm", () => {
  it("renders form", () => {
    const { container } = render(<AbuseReportForm targetName="BadApp" onSubmit={vi.fn()} onCancel={vi.fn()} />);
    expect(container.textContent).toContain("Report BadApp");
    expect(container.querySelector("select")).toBeTruthy();
    expect(container.querySelector("textarea")).toBeTruthy();
  });
  it("submit disabled initially", () => {
    const { container } = render(<AbuseReportForm targetName="X" onSubmit={vi.fn()} onCancel={vi.fn()} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Submit Report") as HTMLButtonElement;
    expect(btn.disabled).toBe(true);
  });
  it("cancel calls handler", () => {
    const onCancel = vi.fn();
    const { container } = render(<AbuseReportForm targetName="X" onSubmit={vi.fn()} onCancel={onCancel} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Cancel")!;
    fireEvent.click(btn);
    expect(onCancel).toHaveBeenCalled();
  });
});
