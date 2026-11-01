import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV70 } from "@/components/platform-v70";
describe("PlatformV70", () => { it("renders", () => {
    const { container } = render(<PlatformV70 />);
    expect(container.textContent).toContain("v70");
    expect(container.textContent).toContain("BIG 70");
}); });
