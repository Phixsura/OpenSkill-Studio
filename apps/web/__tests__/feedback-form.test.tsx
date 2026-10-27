import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeedbackForm } from "@/components/feedback-form";

describe("FeedbackForm", () => {
  it("renders form", () => {
    const { container } = render(<FeedbackForm />);
    expect(container.textContent).toContain("Send Feedback");
    expect(container.querySelector("textarea")).toBeTruthy();
    expect(container.textContent).toContain("bug");
    expect(container.textContent).toContain("feature");
  });
  it("submits feedback", () => {
    const fn = vi.fn();
    const { container } = render(<FeedbackForm onSubmit={fn} />);
    const textarea = container.querySelector("textarea")!;
    fireEvent.change(textarea, { target: { value: "Great platform!" } });
    const submitBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Submit Feedback");
    if (submitBtn) fireEvent.click(submitBtn);
    expect(fn).toHaveBeenCalledWith("feature", "Great platform!", 0);
  });
});
