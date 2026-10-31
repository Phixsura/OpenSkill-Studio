import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV61 } from "@/components/platform-v61";
describe("PlatformV61", () => { it("renders", () => {
    const { container } = render(<PlatformV61 />);
    expect(container.textContent).toContain("v61");
}); });
