import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeedbackWidget } from "@/components/feedback-widget";

describe("FeedbackWidget", () => {
  it("renders and submits", () => {
    const onSubmit = vi.fn();
    const { container, getByText, getByTitle } = render(
      <FeedbackWidget onSubmit={onSubmit} submitted={false} />
    );
    expect(container.textContent).toContain("How was this page?");
    fireEvent.click(getByTitle("Love it"));
    fireEvent.click(getByText("Submit"));
    expect(onSubmit).toHaveBeenCalledWith("love", "");
  });

  it("shows thanks", () => {
    const { container } = render(<FeedbackWidget onSubmit={vi.fn()} submitted={true} />);
    expect(container.textContent).toContain("Thanks");
  });
});
