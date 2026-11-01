import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReviewResponseEditor } from "@/components/review-response-editor";

describe("ReviewResponseEditor", () => {
  it("renders unresponded", () => {
    const review = { review_id: "r1", user_name: "Alice", rating: 3,
      text: "Could be better", has_response: false };
    const { container } = render(<ReviewResponseEditor review={review} onSubmit={vi.fn()} />);
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("Could be better");
    expect(container.querySelector("textarea")).toBeTruthy();
    expect(container.textContent).toContain("Reply");
  });
  it("renders responded", () => {
    const review = { review_id: "r1", user_name: "Bob", rating: 5,
      text: "Great!", has_response: true, response: "Thank you!" };
    const { container } = render(<ReviewResponseEditor review={review} onSubmit={vi.fn()} />);
    expect(container.textContent).toContain("Your response:");
    expect(container.textContent).toContain("Thank you!");
    expect(container.querySelector("textarea")).toBeFalsy();
  });
});
