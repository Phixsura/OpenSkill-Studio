import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ReviewWorkflowCard from "../src/components/review-workflow-card";

const submissions = [
  {
    submission_id: "s1",
    app_version: "2.0.0",
    status: "approved" as const,
    reviewer: "alice",
    feedback: "Looks good!",
  },
  {
    submission_id: "s2",
    app_version: "2.1.0",
    status: "in_review" as const,
    reviewer: "bob",
    feedback: "",
  },
  {
    submission_id: "s3",
    app_version: "3.0.0",
    status: "rejected" as const,
    reviewer: "alice",
    feedback: "Security issue",
  },
];

describe("ReviewWorkflowCard", () => {
  it("renders header", () => {
    const { container } = render(<ReviewWorkflowCard submissions={submissions} appName="My App" />);
    expect(container.textContent).toContain("Review Workflow");
  });

  it("shows pending count", () => {
    const { container } = render(<ReviewWorkflowCard submissions={submissions} appName="App" />);
    expect(container.textContent).toContain("1 pending");
  });

  it("renders versions and statuses", () => {
    const { container } = render(<ReviewWorkflowCard submissions={submissions} appName="App" />);
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("approved");
    expect(container.textContent).toContain("in review");
  });

  it("shows reviewer", () => {
    const { container } = render(<ReviewWorkflowCard submissions={submissions} appName="App" />);
    expect(container.textContent).toContain("alice");
  });

  it("shows feedback", () => {
    const { container } = render(<ReviewWorkflowCard submissions={submissions} appName="App" />);
    expect(container.textContent).toContain("Security issue");
  });

  it("shows empty state", () => {
    const { container } = render(<ReviewWorkflowCard submissions={[]} appName="App" />);
    expect(container.textContent).toContain("No submissions");
  });
});
