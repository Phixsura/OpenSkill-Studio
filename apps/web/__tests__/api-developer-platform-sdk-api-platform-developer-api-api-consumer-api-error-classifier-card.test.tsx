import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-error-classifier-card";

describe("ErrorClassifierCard", () => {
  it("shows categories", () => {
    const categories = [{ category: "auth", count: 50 }, { category: "server", count: 10 }];
    const { container } = render(<Card categories={categories} totalErrors={60} appName="App" />);
    expect(container.textContent).toContain("Error Classifier");
    expect(container.textContent).toContain("60");
    expect(container.textContent).toContain("auth");
    expect(container.textContent).toContain("50");
  });
  it("shows empty", () => {
    const { container } = render(<Card categories={[]} totalErrors={0} appName="App" />);
    expect(container.textContent).toContain("No errors classified");
  });
});
