import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BatchProgressBar } from "@/components/batch-progress-bar";

describe("BatchProgressBar", () => {
  it("shows progress", () => {
    const { container } = render(<BatchProgressBar total={10} completed={7} failed={0} operation="Restart" />);
    expect(container.textContent).toContain("7/10");
    expect(container.textContent).toContain("Restart");
  });
  it("shows failures", () => {
    const { container } = render(<BatchProgressBar total={5} completed={3} failed={2} operation="Update" />);
    expect(container.textContent).toContain("2 failed");
  });
  it("shows complete", () => {
    const { container } = render(<BatchProgressBar total={5} completed={5} failed={0} operation="Done" />);
    expect(container.textContent).toContain("✅");
  });
});
