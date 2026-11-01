import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV79 } from "@/components/platform-v79";
describe("PlatformV79", () => { it("renders", () => {
    const { container } = render(<PlatformV79 />);
    expect(container.textContent).toContain("v79");
}); });
