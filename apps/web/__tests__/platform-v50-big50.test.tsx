import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV50Big50 } from "@/components/platform-v50-big50";
describe("PlatformV50Big50", () => { it("renders", () => {
    const { container } = render(<PlatformV50Big50 />);
    expect(container.textContent).toContain("v50");
    expect(container.textContent).toContain("BIG 50");
    expect(container.textContent).toContain("320K");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
