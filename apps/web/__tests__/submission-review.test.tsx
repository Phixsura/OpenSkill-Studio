import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SubmissionReview } from "@/components/submission-review";

describe("SubmissionReview", () => {
  const checks = [
    { id: "manifest", label: "Valid manifest", auto: true, pass: true },
    { id: "docs", label: "Documentation", auto: false, pass: false },
  ];
  it("renders checklist", () => {
    const { container } = render(
      <SubmissionReview checks={checks} passed={1} total={2} readyForReview={false} score={50} onSubmit={vi.fn()} />
    );
    expect(container.textContent).toContain("Valid manifest");
    expect(container.textContent).toContain("Documentation");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("Complete checklist first");
  });
});
