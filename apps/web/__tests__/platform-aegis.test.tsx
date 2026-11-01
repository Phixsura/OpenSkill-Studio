import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformAegis } from "@/components/platform-aegis";
describe("PlatformAegis", () => { it("renders", () => {
    const { container } = render(<PlatformAegis />);
    expect(container.textContent).toContain("AEGIS");
    expect(container.textContent).toContain("DIVINE");
}); });
