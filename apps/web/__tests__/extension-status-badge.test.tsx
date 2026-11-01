import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExtensionStatusBadge } from "@/components/extension-status-badge";
describe("ExtensionStatusBadge", () => {
  it("renders active", () => {
    const { container } = render(<ExtensionStatusBadge status="active" />);
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("✅");
  });
  it("renders suspended", () => {
    const { container } = render(<ExtensionStatusBadge status="suspended" />);
    expect(container.textContent).toContain("⛔");
  });
});
