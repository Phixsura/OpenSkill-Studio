import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV53 } from "@/components/platform-v53";
describe("PlatformV53", () => { it("renders", () => {
    const { container } = render(<PlatformV53 />);
    expect(container.textContent).toContain("v53");
}); });
