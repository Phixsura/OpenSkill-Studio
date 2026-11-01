import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SubmissionWorkflowPanel } from "@/components/submission-workflow-panel";

const fullChecklist = {
  hasManifest: true, hasDescription: true, hasIcon: true,
  hasScreenshots: true, hasPrivacyPolicy: true,
  passesSecurityScan: true, passesContentReview: true,
  completionPercent: 100,
};

const partialChecklist = { ...fullChecklist, hasIcon: false, hasScreenshots: false, completionPercent: 71 };

describe("SubmissionWorkflowPanel", () => {
  it("renders submission with checklist", () => {
    const sub = { id: "s1", extensionName: "MyExt", version: "1.0.0",
      status: "draft" as const, checklist: partialChecklist, revision: 1 };
    const { container } = render(<SubmissionWorkflowPanel submission={sub} />);
    expect(container.textContent).toContain("MyExt v1.0.0");
    expect(container.textContent).toContain("71%");
    expect(container.textContent).toContain("Draft");
  });

  it("shows submit button when checklist complete", () => {
    const onSubmit = vi.fn();
    const sub = { id: "s1", extensionName: "MyExt", version: "1.0.0",
      status: "draft" as const, checklist: fullChecklist, revision: 1 };
    const { getByText } = render(<SubmissionWorkflowPanel submission={sub} onSubmit={onSubmit} />);
    fireEvent.click(getByText("Submit for Review"));
    expect(onSubmit).toHaveBeenCalled();
  });

  it("shows publish button when approved", () => {
    const onPublish = vi.fn();
    const sub = { id: "s1", extensionName: "MyExt", version: "1.0.0",
      status: "approved" as const, checklist: fullChecklist, revision: 1 };
    const { getByText } = render(<SubmissionWorkflowPanel submission={sub} onPublish={onPublish} />);
    fireEvent.click(getByText("Publish to Marketplace"));
    expect(onPublish).toHaveBeenCalled();
  });

  it("shows rejection reason", () => {
    const sub = { id: "s1", extensionName: "MyExt", version: "1.0.0",
      status: "rejected" as const, checklist: fullChecklist, revision: 2,
      rejectionReason: "Icon resolution too low" };
    const { container } = render(<SubmissionWorkflowPanel submission={sub} />);
    expect(container.textContent).toContain("Icon resolution too low");
    expect(container.textContent).toContain("Revision #2");
  });
});
