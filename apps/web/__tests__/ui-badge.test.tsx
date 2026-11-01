import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UiBadge } from "@/components/ui-badge";

describe("UiBadge", () => {
  it("renders badge", () => {
    const { container } = render(<UiBadge label="Active" variant="success" dot={true} />);
    expect(container.textContent).toContain("Active");
  });
  it("renders with icon", () => {
    const { container } = render(<UiBadge label="Pro" variant="primary" icon="⭐" />);
    expect(container.textContent).toContain("Pro");
    expect(container.textContent).toContain("⭐");
  });
});
