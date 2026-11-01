import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformPrism } from "@/components/platform-prism";
describe("PlatformPrism", () => { it("renders", () => {
    const { container } = render(<PlatformPrism />);
    expect(container.textContent).toContain("PRISM");
    expect(container.textContent).toContain("Backend");
    expect(container.textContent).toContain("Security");
}); });
