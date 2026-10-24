import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV64 } from "@/components/platform-v64";
describe("PlatformV64", () => { it("renders", () => {
    const { container } = render(<PlatformV64 />);
    expect(container.textContent).toContain("v64");
}); });
