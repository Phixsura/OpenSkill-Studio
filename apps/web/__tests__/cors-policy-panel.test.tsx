import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CorsPolicyPanel } from "@/components/cors-policy-panel";

describe("CorsPolicyPanel", () => {
  it("renders", () => {
    const { container } = render(
      <CorsPolicyPanel policies={[
        { origin: "https://app.example.com", methods: ["GET", "POST"], credentials: true, maxAge: 3600 },
        { origin: "*", methods: ["GET"], credentials: false, maxAge: 600 },
      ]} />
    );
    expect(container.textContent).toContain("CORS Policies");
    expect(container.textContent).toContain("2 origins");
    expect(container.textContent).toContain("https://app.example.com");
    expect(container.textContent).toContain("GET, POST");
    expect(container.textContent).toContain("credentials");
    expect(container.textContent).toContain("*");
  });
});
