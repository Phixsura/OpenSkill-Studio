import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV26 } from "@/components/platform-v26";
describe("PlatformV26", () => { it("renders", () => {
    const { container } = render(<PlatformV26 />);
    expect(container.textContent).toContain("v26");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
