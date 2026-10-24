import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV40 } from "@/components/platform-v40";
describe("PlatformV40", () => { it("renders", () => {
    const { container } = render(<PlatformV40 />);
    expect(container.textContent).toContain("v40");
    expect(container.textContent).toContain("BIG 40");
}); });
