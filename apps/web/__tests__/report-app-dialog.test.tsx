import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReportAppDialog } from "@/components/report-app-dialog";

describe("ReportAppDialog", () => {
  it("renders dialog", () => {
    const { container } = render(
      <ReportAppDialog appName="Bad App" onSubmit={vi.fn()} onCancel={vi.fn()}
        reasons={[
          { id: "spam", label: "Spam" },
          { id: "malware", label: "Malicious" },
        ]} />
    );
    expect(container.textContent).toContain("Report Bad App");
    expect(container.textContent).toContain("Spam");
    expect(container.textContent).toContain("Malicious");
    expect(container.textContent).toContain("Submit Report");
  });
});
