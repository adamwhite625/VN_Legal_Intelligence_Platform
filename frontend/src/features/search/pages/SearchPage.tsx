import MainLayout from "@/shared/layout/MainLayout";
import SearchBar from "../components/SearchBar";
import ResultList from "../components/ResultList";
import BrowseCategories from "../components/BrowseCategories";
import { useSearchParams } from "react-router-dom";
import { useEffect } from "react";
import { useSearchStore } from "../model/searchStore";

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { keyword, setKeyword } = useSearchStore();

  useEffect(() => {
    const urlKeyword = searchParams.get("keyword") || "";

    if (urlKeyword) setKeyword(urlKeyword);
  }, []);

  useEffect(() => {
    setSearchParams({
      keyword,
    });
  }, [keyword, setSearchParams]);

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Search Bar - Full Width */}
        <SearchBar />

        {/* Results or Categories */}
        {keyword.trim() ? <ResultList /> : <BrowseCategories />}
      </div>
    </MainLayout>
  );
}
