import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV30 } from "@/components/platform-v30";
describe("PlatformV30", () => { it("renders", () => {
    const { container } = render(<PlatformV30 />);
    expect(container.textContent).toContain("v30");
    expect(container.textContent).toContain("BIG 30");
}); });
