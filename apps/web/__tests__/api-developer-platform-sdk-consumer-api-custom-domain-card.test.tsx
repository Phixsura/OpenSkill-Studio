import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CustomDomainCard from "../src/components/api-developer-platform-sdk-consumer-api-custom-domain-card";

describe("CustomDomainCard", () => {
  it("renders title and domains", () => {
    const { container } = render(<CustomDomainCard />);
    expect(container.textContent).toContain("Custom Domains");
    expect(container.textContent).toContain("api.acme.com");
    expect(container.textContent).toContain("staging-api.acme.com");
  });

  it("shows SSL status", () => {
    const { container } = render(<CustomDomainCard />);
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("pending");
    expect(container.textContent).toContain("1/3 SSL active");
  });
});
