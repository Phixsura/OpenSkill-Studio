import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import SecretRotationCard from "../src/components/api-developer-platform-sdk-consumer-api-secret-rotation-card";

describe("SecretRotationCard", () => {
  it("renders title and versions", () => {
    const { container } = render(<SecretRotationCard />);
    expect(container.textContent).toContain("Secret Rotation");
    expect(container.textContent).toContain("v3");
    expect(container.textContent).toContain("v1");
  });

  it("shows statuses and valid count", () => {
    const { container } = render(<SecretRotationCard />);
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("grace");
    expect(container.textContent).toContain("2 valid versions");
  });
});
