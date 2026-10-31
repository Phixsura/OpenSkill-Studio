import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformAurora } from "@/components/platform-aurora";
describe("PlatformAurora", () => { it("renders", () => {
    const { container } = render(<PlatformAurora />);
    expect(container.textContent).toContain("AURORA");
    expect(container.textContent).toContain("SPECTACULAR");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
