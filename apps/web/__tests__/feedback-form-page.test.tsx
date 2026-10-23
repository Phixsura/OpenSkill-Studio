import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeedbackFormPage } from "@/components/feedback-form-page";

describe("FeedbackFormPage", () => {
  const categories = [
    { id: "bug", label: "Bug", icon: "🐛", description: "Report a bug" },
    { id: "feature", label: "Feature", icon: "💡", description: "Request feature" },
  ];
  it("renders", () => {
    const { container } = render(<FeedbackFormPage categories={categories} onSubmit={vi.fn()} />);
    expect(container.textContent).toContain("Send Feedback");
    expect(container.textContent).toContain("Bug");
    expect(container.textContent).toContain("Feature");
    expect(container.querySelector("input")).toBeTruthy();
    expect(container.querySelector("textarea")).toBeTruthy();
  });
});
