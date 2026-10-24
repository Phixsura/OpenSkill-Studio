import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV72 } from "@/components/platform-v72";
describe("PlatformV72", () => { it("renders", () => {
    const { container } = render(<PlatformV72 />);
    expect(container.textContent).toContain("v72");
}); });
