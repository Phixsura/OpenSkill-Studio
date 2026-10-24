import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV46 } from "@/components/platform-v46";
describe("PlatformV46", () => { it("renders", () => {
    const { container } = render(<PlatformV46 />);
    expect(container.textContent).toContain("v46");
}); });
