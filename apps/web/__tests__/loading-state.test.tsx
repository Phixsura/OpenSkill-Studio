import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LoadingState } from "@/components/loading-state";

describe("LoadingState", () => {
  it("spinner", () => {
    const { container } = render(
      <LoadingState variant="spinner" message="Loading..." progressPct={null} showProgress={false} />
    );
    expect(container.textContent).toContain("Loading...");
    expect(container.querySelector(".animate-spin")).toBeTruthy();
  });
  it("progress", () => {
    const { container } = render(
      <LoadingState variant="progress" message="Deploying..." progressPct={65} showProgress={true} />
    );
    expect(container.textContent).toContain("65%");
    expect(container.textContent).toContain("Deploying...");
  });
  it("dots", () => {
    const { container } = render(
      <LoadingState variant="dots" message={null} progressPct={null} showProgress={false} />
    );
    expect(container.querySelectorAll(".animate-bounce").length).toBe(3);
  });
});
