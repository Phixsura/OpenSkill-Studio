import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV500Panel } from "@/components/platform-v500-panel";
describe("PlatformV500Panel", () => { it("renders", () => {
    const { container } = render(<PlatformV500Panel />);
    expect(container.textContent).toContain("v500");
    expect(container.textContent).toContain("HALF A THOUSAND");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
