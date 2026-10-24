import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeedbackForm } from "@/components/feedback-form";

describe("FeedbackForm", () => {
  it("shows type buttons", () => {
    const { container } = render(<FeedbackForm onSubmit={vi.fn()} />);
    expect(container.textContent).toContain("bug");
    expect(container.textContent).toContain("feature request");
  });
  it("has textarea", () => {
    const { container } = render(<FeedbackForm onSubmit={vi.fn()} />);
    expect(container.querySelector("textarea")).toBeTruthy();
  });
  it("has send button", () => {
    const { container } = render(<FeedbackForm onSubmit={vi.fn()} />);
    expect(container.textContent).toContain("Send");
  });
});
