import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RelativeTime } from "@/components/relative-time";

describe("RelativeTime", () => {
  it("renders time", () => {
    const { container } = render(<RelativeTime value="5m ago" label="Updated" />);
    expect(container.textContent).toContain("Updated:");
    expect(container.textContent).toContain("5m ago");
  });

  it("renders without label", () => {
    const { container } = render(<RelativeTime value="just now" />);
    expect(container.textContent).toContain("just now");
  });
});
