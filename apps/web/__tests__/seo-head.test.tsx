import { describe, expect, it } from "vitest";
import { SeoHead } from "@/components/seo-head";

describe("SeoHead", () => {
  it("is a function component", () => {
    expect(typeof SeoHead).toBe("function");
  });
  it("accepts required props", () => {
    // Verify component doesn't throw with valid props
    const result = SeoHead({ title: "Test", description: "Desc" });
    expect(result).toBeTruthy();
  });
  it("accepts optional props", () => {
    const result = SeoHead({ title: "X", description: "Y", canonical: "https://x.com", ogImage: "https://img.com/x.png" });
    expect(result).toBeTruthy();
  });
});
