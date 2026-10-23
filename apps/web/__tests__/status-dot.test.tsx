import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusDot } from "@/components/status-dot";

describe("StatusDot", () => {
  it("renders with label", () => {
    const { container } = render(<StatusDot color="green" label="Online" pulse={true} />);
    expect(container.textContent).toContain("Online");
    expect(container.querySelector(".animate-pulse")).toBeTruthy();
  });
  it("hides label", () => {
    const { container } = render(<StatusDot color="red" label="Error" pulse={false} showLabel={false} />);
    expect(container.textContent).not.toContain("Error");
  });
});
