import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformOlympus } from "@/components/platform-olympus";
describe("PlatformOlympus", () => { it("renders", () => {
    const { container } = render(<PlatformOlympus />);
    expect(container.textContent).toContain("OLYMPUS");
    expect(container.textContent).toContain("Zeus");
}); });
