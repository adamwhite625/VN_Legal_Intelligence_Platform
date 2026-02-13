import { useSearchStore } from "../model/searchStore";

export default function SearchBar() {
  const { keyword, setKeyword } = useSearchStore();

  return (
    <div className="bg-white p-4 rounded-xl shadow">
      <input
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
        className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="Tìm kiếm điều luật..."
      />
    </div>
  );
}
