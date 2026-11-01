import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformPhoenix } from "@/components/platform-phoenix";
describe("PlatformPhoenix", () => { it("renders", () => {
    const { container } = render(<PlatformPhoenix />);
    expect(container.textContent).toContain("PHOENIX");
    expect(container.textContent).toContain("BLAZING GLORY");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
