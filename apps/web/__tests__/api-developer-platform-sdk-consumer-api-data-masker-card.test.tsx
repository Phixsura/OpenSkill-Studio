import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DataMaskerCard from "../src/components/api-developer-platform-sdk-consumer-api-data-masker-card";

describe("DataMaskerCard", () => {
  it("renders title and rules", () => {
    const { container } = render(<DataMaskerCard />);
    expect(container.textContent).toContain("Data Masker");
    expect(container.textContent).toContain("password");
    expect(container.textContent).toContain("credit_card");
  });

  it("shows mask types and stats", () => {
    const { container } = render(<DataMaskerCard />);
    expect(container.textContent).toContain("full");
    expect(container.textContent).toContain("hash");
    expect(container.textContent).toContain("4 rules");
    expect(container.textContent).toContain("12,450 fields masked");
  });
});
