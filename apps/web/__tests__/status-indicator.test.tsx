import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusIndicator } from "@/components/status-indicator";

describe("StatusIndicator", () => {
  it("shows operational", () => {
    const { container } = render(<StatusIndicator status="operational" />);
    expect(container.textContent).toContain("operational");
  });
  it("shows custom label", () => {
    const { container } = render(<StatusIndicator status="degraded" label="Partially down" />);
    expect(container.textContent).toContain("Partially down");
  });
  it("has colored dot", () => {
    const { container } = render(<StatusIndicator status="outage" />);
    expect(container.querySelector("[class*='bg-red']")).toBeTruthy();
  });
});
