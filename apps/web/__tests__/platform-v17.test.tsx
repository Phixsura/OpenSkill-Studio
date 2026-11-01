import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV17 } from "@/components/platform-v17";
describe("PlatformV17", () => { it("renders", () => {
    const { container } = render(<PlatformV17 />);
    expect(container.textContent).toContain("v17.0");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
