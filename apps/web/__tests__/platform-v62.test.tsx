import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV62 } from "@/components/platform-v62";
describe("PlatformV62", () => { it("renders", () => {
    const { container } = render(<PlatformV62 />);
    expect(container.textContent).toContain("v62");
}); });
