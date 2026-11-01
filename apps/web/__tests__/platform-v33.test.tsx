import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV33 } from "@/components/platform-v33";
describe("PlatformV33", () => { it("renders", () => {
    const { container } = render(<PlatformV33 />);
    expect(container.textContent).toContain("v33");
}); });
