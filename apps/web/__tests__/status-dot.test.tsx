import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusDot } from "@/components/status-dot";

describe("StatusDot", () => {
  it("renders with label", () => {
    const { container } = render(<StatusDot status="green" label="Operational" icon="🟢" />);
    expect(container.textContent).toContain("Operational");
  });
  it("renders without label", () => {
    const { container } = render(<StatusDot status="red" label="Outage" icon="🔴" showLabel={false} />);
    expect(container.textContent).not.toContain("Outage");
  });
});
