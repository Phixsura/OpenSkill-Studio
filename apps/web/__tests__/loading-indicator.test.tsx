import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LoadingIndicator } from "@/components/loading-indicator";

describe("LoadingIndicator", () => {
  it("renders spinner", () => {
    const { container } = render(<LoadingIndicator type="spinner" label="Loading..." />);
    expect(container.textContent).toContain("Loading...");
    expect(container.querySelector(".animate-spin")).toBeTruthy();
  });

  it("renders dots", () => {
    const { container } = render(<LoadingIndicator type="dots" />);
    expect(container.querySelectorAll(".animate-pulse").length).toBe(3);
  });

  it("renders progress bar", () => {
    const { container } = render(<LoadingIndicator type="progress_bar" />);
    expect(container.querySelector(".animate-pulse")).toBeTruthy();
  });
});
