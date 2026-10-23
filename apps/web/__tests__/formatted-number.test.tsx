import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FormattedNumber } from "@/components/formatted-number";

describe("FormattedNumber", () => {
  it("compact", () => {
    const { container } = render(<FormattedNumber value={5400} />);
    expect(container.textContent).toContain("5.4K");
  });
  it("currency", () => {
    const { container } = render(<FormattedNumber value={1234.5} style="currency" />);
    expect(container.textContent).toContain("$");
    expect(container.textContent).toContain("1,234.50");
  });
  it("percentage", () => {
    const { container } = render(<FormattedNumber value={99.5} style="percentage" />);
    expect(container.textContent).toContain("99.5%");
  });
  it("prefix suffix", () => {
    const { container } = render(<FormattedNumber value={42} prefix="~" suffix=" items" />);
    expect(container.textContent).toContain("~42 items");
  });
});
