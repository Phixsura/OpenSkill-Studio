import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformQuantumLeap } from "@/components/platform-quantum-leap";
describe("PlatformQuantumLeap", () => { it("renders", () => {
    const { container } = render(<PlatformQuantumLeap />);
    expect(container.textContent).toContain("QUANTUM LEAP");
    expect(container.textContent).toContain("100% perfect");
}); });
