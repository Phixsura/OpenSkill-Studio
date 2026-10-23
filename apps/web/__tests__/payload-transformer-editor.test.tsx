import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PayloadTransformerEditor } from "@/components/payload-transformer-editor";

describe("PayloadTransformerEditor", () => {
  it("renders transformer", () => {
    const { container } = render(
      <PayloadTransformerEditor inputPayload='{"name": "Alice"}' outputPayload='{"userName": "Alice"}'
        onTransform={vi.fn()} />
    );
    expect(container.textContent).toContain("Payload Transformer");
    expect(container.textContent).toContain("Input");
    expect(container.textContent).toContain("Output");
    expect(container.textContent).toContain("userName");
  });
});
