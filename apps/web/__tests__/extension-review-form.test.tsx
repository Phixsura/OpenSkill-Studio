import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExtensionReviewForm } from "@/components/extension-review-form";

describe("ExtensionReviewForm", () => {
  it("renders form fields", () => {
    const { container, getByPlaceholderText } = render(
      <ExtensionReviewForm extensionName="Slack Bot" />
    );
    expect(container.textContent).toContain("Review Slack Bot");
    expect(getByPlaceholderText("Summarize your experience...")).toBeDefined();
    expect(getByPlaceholderText("Tell others about your experience...")).toBeDefined();
  });

  it("disables submit without rating and title", () => {
    const { getByText } = render(<ExtensionReviewForm extensionName="Test" />);
    const btn = getByText("Submit Review");
    expect(btn.hasAttribute("disabled")).toBe(true);
  });

  it("submits review and shows confirmation", () => {
    const onSubmit = vi.fn();
    const { getByText, getByPlaceholderText, container } = render(
      <ExtensionReviewForm extensionName="Test" onSubmit={onSubmit} />
    );
    // Click 4th star
    const stars = container.querySelectorAll(".text-2xl");
    fireEvent.click(stars[3]);
    // Fill title
    fireEvent.change(getByPlaceholderText("Summarize your experience..."), { target: { value: "Great tool!" } });
    // Submit
    fireEvent.click(getByText("Submit Review"));
    expect(onSubmit).toHaveBeenCalledWith({ rating: 4, title: "Great tool!", body: "" });
    expect(container.textContent).toContain("Thank you");
  });
});
