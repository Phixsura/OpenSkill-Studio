"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

interface Category {
  key: string;
  icon: string;
  label: string;
  description: string;
  app_count: number;
}

export default function CategoriesPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["marketplace-categories"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/v1/marketplace/categories`);
      return res.json() as Promise<{ data: Category[] }>;
    },
  });

  const categories = data?.data ?? [];

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <h1 className="mb-2 text-3xl font-bold">Browse by Category</h1>
      <p className="mb-8 text-gray-600 dark:text-gray-400">
        Explore apps organized by what they do
      </p>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-32 animate-pulse rounded-xl bg-gray-200 dark:bg-gray-700" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {categories.map((cat) => (
            <Link
              key={cat.key}
              href={`/marketplace/apps?category=${cat.key}`}
              className="group rounded-xl border p-6 transition-all hover:border-blue-500 hover:shadow-lg dark:border-gray-700"
            >
              <div className="mb-3 text-4xl">{cat.icon}</div>
              <h3 className="text-lg font-semibold group-hover:text-blue-600">{cat.label}</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{cat.description}</p>
              <p className="mt-3 text-sm font-medium text-blue-600">
                {cat.app_count} app{cat.app_count !== 1 ? "s" : ""} →
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
