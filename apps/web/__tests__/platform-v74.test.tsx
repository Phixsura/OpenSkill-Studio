import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV74 } from "@/components/platform-v74";
describe("PlatformV74", () => { it("renders", () => {
    const { container } = render(<PlatformV74 />);
    expect(container.textContent).toContain("v74");
}); });
