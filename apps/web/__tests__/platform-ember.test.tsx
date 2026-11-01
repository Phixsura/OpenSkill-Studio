import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformEmber } from "@/components/platform-ember";
describe("PlatformEmber", () => { it("renders", () => {
    const { container } = render(<PlatformEmber />);
    expect(container.textContent).toContain("EMBER");
    expect(container.textContent).toContain("0 extinguished");
}); });
