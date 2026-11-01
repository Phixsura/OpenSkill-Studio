import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReqInspector } from "@/components/req-inspector";

describe("ReqInspector", () => {
  it("renders", () => {
    const { container } = render(
      <ReqInspector method="POST" path="/api/users" headerCount={5}
        contentType="application/json" authType="bearer" bodySize={128} paramCount={2} />
    );
    expect(container.textContent).toContain("POST");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("bearer");
    expect(container.textContent).toContain("128B");
  });
});
