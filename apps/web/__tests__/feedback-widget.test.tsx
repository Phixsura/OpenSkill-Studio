import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeedbackWidget } from "@/components/feedback-widget";

describe("FeedbackWidget", () => {
  it("renders emoji rating", () => {
    const { container } = render(<FeedbackWidget onSubmit={vi.fn()} />);
    expect(container.textContent).toContain("How was your experience");
    expect(container.textContent).toContain("🤩");
    expect(container.querySelectorAll("button").length).toBe(6); // 5 emojis + submit
  });
  it("submit after rating", () => {
    const fn = vi.fn();
    const { container } = render(<FeedbackWidget onSubmit={fn} />);
    // Click 5-star emoji
    fireEvent.click(container.querySelectorAll("button")[4]);
    // Click submit
    const submit = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Submit Feedback")!;
    fireEvent.click(submit);
    expect(fn).toHaveBeenCalledWith("", 5);
  });
});
