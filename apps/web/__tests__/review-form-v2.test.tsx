import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReviewFormV2 } from "@/components/review-form-v2";

describe("ReviewFormV2", () => {
  it("renders form", () => {
    const { container } = render(<ReviewFormV2 appName="SuperApp" onSubmit={vi.fn()} />);
    expect(container.textContent).toContain("Review SuperApp");
    expect(container.textContent).toContain("Rating");
    expect(container.textContent).toContain("Pros");
    expect(container.textContent).toContain("Cons");
    expect(container.querySelector("button:last-of-type")?.textContent).toContain("Submit Review");
  });
  it("submit disabled initially", () => {
    const { container } = render(<ReviewFormV2 appName="X" onSubmit={vi.fn()} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Submit")) as HTMLButtonElement;
    expect(btn.disabled).toBe(true);
  });
});
