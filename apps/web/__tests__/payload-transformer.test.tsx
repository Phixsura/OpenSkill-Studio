import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PayloadTransformer } from "@/components/payload-transformer";

describe("PayloadTransformer", () => {
  it("renders transformer", () => {
    const { container } = render(
      <PayloadTransformer mappedFields={2} nullFields={0}
        original={{ user: { name: "Alice" }, action: "login" }}
        transformed={{ username: "Alice", event: "login" }} />
    );
    expect(container.textContent).toContain("Payload Transformer");
    expect(container.textContent).toContain("2 mapped");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("Input");
    expect(container.textContent).toContain("Output");
  });
});
