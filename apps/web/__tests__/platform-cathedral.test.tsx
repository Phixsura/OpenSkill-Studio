import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformCathedral } from "@/components/platform-cathedral";
describe("PlatformCathedral", () => { it("renders", () => {
    const { container } = render(<PlatformCathedral />);
    expect(container.textContent).toContain("CATHEDRAL");
    expect(container.textContent).toContain("DORA Elite");
}); });
