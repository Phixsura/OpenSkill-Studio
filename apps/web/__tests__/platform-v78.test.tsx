import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV78 } from "@/components/platform-v78";
describe("PlatformV78", () => { it("renders", () => {
    const { container } = render(<PlatformV78 />);
    expect(container.textContent).toContain("v78");
}); });
