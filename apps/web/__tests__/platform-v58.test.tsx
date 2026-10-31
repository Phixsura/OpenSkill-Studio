import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV58 } from "@/components/platform-v58";
describe("PlatformV58", () => { it("renders", () => {
    const { container } = render(<PlatformV58 />);
    expect(container.textContent).toContain("v58");
    expect(container.textContent).toContain("322K");
}); });
