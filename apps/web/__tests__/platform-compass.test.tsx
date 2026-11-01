import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformCompass } from "@/components/platform-compass";
describe("PlatformCompass", () => { it("renders", () => {
    const { container } = render(<PlatformCompass />);
    expect(container.textContent).toContain("COMPASS");
    expect(container.textContent).toContain("Quality");
    expect(container.textContent).toContain("Innovation");
}); });
