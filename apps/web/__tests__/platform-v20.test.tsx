import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV20 } from "@/components/platform-v20";
describe("PlatformV20", () => { it("renders", () => {
    const { container } = render(<PlatformV20 />);
    expect(container.textContent).toContain("v20.0");
    expect(container.textContent).toContain("BIG 20");
}); });
