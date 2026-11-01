import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LoadingSpinner } from "@/components/loading-spinner";

describe("LoadingSpinner", () => {
  it("renders", () => {
    const { container } = render(<LoadingSpinner />);
    expect(container.querySelector("[class*='animate-spin']")).toBeTruthy();
  });
  it("shows label", () => {
    const { container } = render(<LoadingSpinner label="Loading apps..." />);
    expect(container.textContent).toContain("Loading apps");
  });
  it("no label by default", () => {
    const { container } = render(<LoadingSpinner />);
    expect(container.textContent).toBe("");
  });
});
