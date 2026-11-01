import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WhTransformPanel } from "@/components/wh-transform-panel";
describe("WhTransformPanel", () => {
  it("renders", () => {
    const { container } = render(
      <WhTransformPanel fieldsMapped={5} fieldsMissing={1} payloadSize={2048} />
    );
    expect(container.textContent).toContain("Payload Transform");
    expect(container.textContent).toContain("5 mapped");
    expect(container.textContent).toContain("1 missing");
    expect(container.textContent).toContain("2048B");
  });
});
