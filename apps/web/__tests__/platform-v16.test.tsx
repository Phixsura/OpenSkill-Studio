import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV16 } from "@/components/platform-v16";
describe("PlatformV16", () => { it("renders", () => {
    const { container } = render(<PlatformV16 />);
    expect(container.textContent).toContain("v16.0");
    expect(container.textContent).toContain("BEYOND 300K");
}); });
