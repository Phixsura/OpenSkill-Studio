import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DocGeneratorCard from "../src/components/api-developer-platform-sdk-consumer-api-doc-generator-card";

describe("DocGeneratorCard", () => {
  it("renders title and endpoints", () => {
    const { container } = render(<DocGeneratorCard />);
    expect(container.textContent).toContain("Doc Generator");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("List all users");
  });

  it("shows active and deprecated counts", () => {
    const { container } = render(<DocGeneratorCard />);
    expect(container.textContent).toContain("2 active");
    expect(container.textContent).toContain("1 deprecated");
  });
});
