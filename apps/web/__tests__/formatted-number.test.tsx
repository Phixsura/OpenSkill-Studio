import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FormattedNumber } from "@/components/formatted-number";

describe("FormattedNumber", () => {
  it("renders compact", () => {
    const { container } = render(<FormattedNumber value={2500000} format="compact" />);
    expect(container.textContent).toContain("2.5M");
  });
  it("renders percentage", () => {
    const { container } = render(<FormattedNumber value={99.5} format="percentage" />);
    expect(container.textContent).toContain("99.5%");
  });
  it("renders currency", () => {
    const { container } = render(<FormattedNumber value={1500} format="currency" />);
    expect(container.textContent).toContain("$");
    expect(container.textContent).toContain("1,500");
  });
});
