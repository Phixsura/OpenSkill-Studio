import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformSupernova } from "@/components/platform-supernova";
describe("PlatformSupernova", () => { it("renders", () => {
    const { container } = render(<PlatformSupernova />);
    expect(container.textContent).toContain("SUPERNOVA");
    expect(container.textContent).toContain("COSMIC");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
