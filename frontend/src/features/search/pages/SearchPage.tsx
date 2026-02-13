import MainLayout from "@/shared/layout/MainLayout";
import SearchBar from "../components/SearchBar";
import FilterPanel from "../components/FilterPanel";
import ResultList from "../components/ResultList";
import { useSearchParams } from "react-router-dom";
import { useEffect } from "react";
import { useSearchStore } from "../model/searchStore";

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { keyword, type, year, authority, setKeyword, setFilter } =
    useSearchStore();
  useEffect(() => {
    const urlKeyword = searchParams.get("keyword") || "";
    const urlType = searchParams.get("type") || "";
    const urlYear = searchParams.get("year") || "";
    const urlAuthority = searchParams.get("authority") || "";

    setKeyword(urlKeyword);
    setFilter("type", urlType);
    setFilter("year", urlYear);
    setFilter("authority", urlAuthority);
  }, []);

  useEffect(() => {
    setSearchParams({
      keyword,
      type,
      year,
      authority,
    });
  }, [keyword, type, year, authority]);

  return (
    <MainLayout>
      <div className="grid grid-cols-4 gap-6">
        <div className="bg-white p-4 rounded-xl shadow">
          <FilterPanel />
        </div>

        <div className="col-span-3 space-y-6">
          <SearchBar />
          <ResultList />
        </div>
      </div>
    </MainLayout>
  );
}
