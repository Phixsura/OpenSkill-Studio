import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformMosaic } from "@/components/platform-mosaic";
describe("PlatformMosaic", () => { it("renders", () => {
    const { container } = render(<PlatformMosaic />);
    expect(container.textContent).toContain("MOSAIC");
    expect(container.textContent).toContain("906K");
}); });
