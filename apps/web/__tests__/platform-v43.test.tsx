import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV43 } from "@/components/platform-v43";
describe("PlatformV43", () => { it("renders", () => {
    const { container } = render(<PlatformV43 />);
    expect(container.textContent).toContain("v43");
}); });
