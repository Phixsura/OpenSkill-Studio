import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReviewForm } from "@/components/review-form";

describe("ReviewForm", () => {
  it("renders", () => {
    const { container } = render(<ReviewForm onSubmit={vi.fn()} />);
    expect(container.textContent).toContain("Write a Review");
    expect(container.textContent).toContain("Rating");
    expect(container.querySelectorAll("button").length).toBe(6); // 5 stars + submit
    expect(container.querySelector("input")).toBeTruthy();
    expect(container.querySelector("textarea")).toBeTruthy();
    expect(container.textContent).toContain("Submit Review");
    expect(container.textContent).toContain("0/5000");
  });
});
