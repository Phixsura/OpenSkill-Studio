import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV23 } from "@/components/platform-v23";
describe("PlatformV23", () => { it("renders", () => {
    const { container } = render(<PlatformV23 />);
    expect(container.textContent).toContain("v23.0");
}); });
