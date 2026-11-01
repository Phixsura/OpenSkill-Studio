import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV27 } from "@/components/platform-v27";
describe("PlatformV27", () => { it("renders", () => {
    const { container } = render(<PlatformV27 />);
    expect(container.textContent).toContain("v27.0");
}); });
