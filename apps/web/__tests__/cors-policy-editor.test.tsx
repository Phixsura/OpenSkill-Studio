import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CorsPolicyEditor } from "@/components/cors-policy-editor";

describe("CorsPolicyEditor", () => {
  it("renders policy", () => {
    const { container } = render(
      <CorsPolicyEditor origins={["https://app.com", "https://admin.app.com"]}
        methods={["GET", "POST"]} credentials={true} maxAge={86400}
        onAddOrigin={vi.fn()} onRemoveOrigin={vi.fn()} />
    );
    expect(container.textContent).toContain("CORS Policy");
    expect(container.textContent).toContain("https://app.com");
    expect(container.textContent).toContain("GET, POST");
    expect(container.textContent).toContain("Yes");
    expect(container.textContent).toContain("86400s");
  });
});
