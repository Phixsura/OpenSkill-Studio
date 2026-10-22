import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeedbackWidget } from "@/components/feedback-widget";

describe("FeedbackWidget", () => {
  it("shows button initially", () => {
    const { container } = render(<FeedbackWidget onSubmit={vi.fn()} />);
    expect(container.textContent).toContain("💬");
  });
  it("opens form on click", () => {
    const { container } = render(<FeedbackWidget onSubmit={vi.fn()} />);
    fireEvent.click(container.querySelector("button")!);
    expect(container.textContent).toContain("Send Feedback");
    expect(container.textContent).toContain("Bug");
    expect(container.textContent).toContain("Feature");
  });
});
