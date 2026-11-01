import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReportForm } from "@/components/report-form";

describe("ReportForm", () => {
  const reasons = [{ id: "spam", label: "Spam" }, { id: "malware", label: "Malware" }];
  it("renders form", () => {
    const { container } = render(
      <ReportForm appName="BadApp" reasons={reasons} onSubmit={vi.fn()} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("Report BadApp");
    expect(container.textContent).toContain("Spam");
    expect(container.textContent).toContain("Malware");
    expect(container.textContent).toContain("Submit Report");
  });
});
