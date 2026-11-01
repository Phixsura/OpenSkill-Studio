import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReportAbuseForm } from "@/components/report-abuse-form";

describe("ReportAbuseForm", () => {
  it("shows app name", () => {
    const { container } = render(<ReportAbuseForm appName="Bad App" onSubmit={vi.fn()} onCancel={vi.fn()} />);
    expect(container.textContent).toContain("Bad App");
  });
  it("has reason select", () => {
    const { container } = render(<ReportAbuseForm appName="X" onSubmit={vi.fn()} onCancel={vi.fn()} />);
    expect(container.querySelector("select")).toBeTruthy();
    expect(container.querySelectorAll("option").length).toBeGreaterThan(5);
  });
  it("has submit button", () => {
    const { container } = render(<ReportAbuseForm appName="X" onSubmit={vi.fn()} onCancel={vi.fn()} />);
    expect(container.textContent).toContain("Submit Report");
  });
});
