"use client";

import { useState } from "react";

interface AppSearchBarProps {
  onSearch: (query: string) => void;
  onCategoryChange?: (category: string) => void;
  placeholder?: string;
  categories?: string[];
}

export function AppSearchBar({ onSearch, onCategoryChange, placeholder = "Search apps...", categories }: AppSearchBarProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text" value={query} onChange={e => setQuery(e.target.value)}
        placeholder={placeholder}
        className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none dark:border-gray-600 dark:bg-gray-800"
      />
      {categories && onCategoryChange && (
        <select onChange={e => onCategoryChange(e.target.value)}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800">
          <option value="">All Categories</option>
          {categories.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      )}
      <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700">
        Search
      </button>
    </form>
  );
}
