import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnimatedTransition } from "@/components/animated-transition";

describe("AnimatedTransition", () => {
  it("shows content when visible", () => {
    const { container } = render(<AnimatedTransition show={true}><p>Hello</p></AnimatedTransition>);
    expect(container.textContent).toContain("Hello");
  });
  it("hides content when not visible", () => {
    const { container } = render(<AnimatedTransition show={false}><p>Hidden</p></AnimatedTransition>);
    expect(container.textContent).toBe("");
  });
});
