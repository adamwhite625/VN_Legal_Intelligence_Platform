import { useSearchStore } from "../model/searchStore";

export default function SearchBar() {
  const { keyword, setKeyword } = useSearchStore();

  return (
    <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-8 rounded-xl shadow-lg">
      <div className="text-white mb-4">
        <h1 className="text-3xl font-bold mb-1">🔍 Tìm Kiếm Luật</h1>
        <p className="text-blue-100 text-sm">
          Tìm kiếm và khám phá các luật lệ một cách dễ dàng
        </p>
      </div>
      <div className="relative">
        <input
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          className="w-full p-4 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300 text-lg"
          placeholder="Nhập từ khóa: Điều, luật, quyền, ..."
        />
        {keyword && (
          <button
            onClick={() => setKeyword("")}
            className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 text-xl"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
}
