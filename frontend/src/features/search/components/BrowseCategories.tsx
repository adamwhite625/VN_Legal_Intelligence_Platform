import { useSearchStore } from "../model/searchStore";
import { useState, useEffect } from "react";
import { searchLaws, type LawItem } from "../api/searchApi";
import { Link } from "react-router-dom";

interface CategoryWithLaws {
  name: string;
  lawName: string;
  icon: string;
  laws: LawItem[];
  loading: boolean;
  articleCount: number;
}

export default function BrowseCategories() {
  // 5 main laws from raw_law_data.json
  const [categories, setCategories] = useState<CategoryWithLaws[]>([
    {
      name: "📜 Bộ luật Dân sự 2015",
      lawName: "Bộ luật Dân sự 2015",
      icon: "📜",
      laws: [],
      loading: false,
      articleCount: 689,
    },
    {
      name: "⚖️ Bộ luật Hình sự",
      lawName: "Bộ luật Hình sự (Văn bản hợp nhất 2017)",
      icon: "⚖️",
      laws: [],
      loading: false,
      articleCount: 416,
    },
    {
      name: "💼 Luật Doanh nghiệp 2020",
      lawName: "Luật Doanh nghiệp 2020",
      icon: "💼",
      laws: [],
      loading: false,
      articleCount: 218,
    },
    {
      name: "👨‍👩‍👧‍👦 Luật Hôn nhân và Gia đình 2014",
      lawName: "Luật Hôn nhân và Gia đình 2014",
      icon: "👨‍👩‍👧‍👦",
      laws: [],
      loading: false,
      articleCount: 133,
    },
    {
      name: "👷 Bộ luật Lao động 2019",
      lawName: "Bộ luật Lao động 2019",
      icon: "👷",
      laws: [],
      loading: false,
      articleCount: 223,
    },
  ]);

  const { setKeyword } = useSearchStore();

  useEffect(() => {
    loadLawsByCategories();
  }, []);

  const loadLawsByCategories = async () => {
    // Load articles for each law category
    categories.forEach((_, index) => {
      loadCategoryLaws(index);
    });
  };

  const loadCategoryLaws = async (categoryIndex: number) => {
    setCategories((prev) => {
      const updated = [...prev];
      updated[categoryIndex].loading = true;
      return updated;
    });

    try {
      const response = await searchLaws(
        categories[categoryIndex].lawName,
        undefined,
        undefined,
        undefined,
        undefined,
        6, // 6 articles per law category
        "fast",
      );

      setCategories((prev) => {
        const updated = [...prev];
        updated[categoryIndex].laws = response.results;
        updated[categoryIndex].loading = false;
        return updated;
      });
    } catch (error) {
      console.error(`Error loading ${categories[categoryIndex].name}:`, error);
      setCategories((prev) => {
        const updated = [...prev];
        updated[categoryIndex].loading = false;
        return updated;
      });
    }
  };

  const handleCategoryClick = (lawName: string) => {
    setKeyword(lawName);
  };

  return (
    <div className="space-y-12 py-8">
      {/* Main Categories Header */}
      <div>
        <h2 className="text-3xl font-bold text-gray-800 mb-2">
          📚 Khám Phá Bộ Luật
        </h2>
        <p className="text-gray-600 mb-8">
          Duyệt các bộ luật chính theo từng danh mục
        </p>

        {/* Category Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {categories.map((category, index) => (
            <div
              key={index}
              className="bg-white rounded-lg shadow-md hover:shadow-lg transition overflow-hidden border border-gray-100"
            >
              {/* Category Header */}
              <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-4 border-b border-blue-200">
                <button
                  onClick={() => handleCategoryClick(category.lawName)}
                  className="w-full text-left flex items-center justify-between group"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{category.icon}</span>
                    <div>
                      <h3 className="font-bold text-gray-800 text-lg group-hover:text-blue-600 transition">
                        {category.name}
                      </h3>
                      <p className="text-xs text-gray-600">
                        {category.articleCount} điều
                      </p>
                    </div>
                  </div>
                  <span className="text-xl text-gray-500 group-hover:text-blue-600 transition">
                    →
                  </span>
                </button>
              </div>

              {/* Laws List */}
              <div className="p-4 space-y-2">
                {category.loading ? (
                  <div className="flex justify-center py-4">
                    <div className="animate-spin w-5 h-5 border-2 border-blue-200 border-t-blue-600 rounded-full"></div>
                  </div>
                ) : category.laws.length > 0 ? (
                  <>
                    {category.laws.map((law) => (
                      <Link
                        key={law.id}
                        to={`/law/${law.id}`}
                        className="block p-3 rounded-lg bg-gray-50 hover:bg-blue-50 border border-gray-100 hover:border-blue-300 transition"
                      >
                        <div className="flex items-start gap-2">
                          <span className="text-blue-600 font-bold text-sm flex-shrink-0 mt-0.5">
                            {law.id}
                          </span>
                          <div className="min-w-0">
                            <p className="text-sm font-medium text-gray-800 line-clamp-2">
                              {law.title || "Không có tiêu đề"}
                            </p>
                          </div>
                        </div>
                      </Link>
                    ))}
                    <button
                      onClick={() => handleCategoryClick(category.lawName)}
                      className="w-full mt-2 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded font-medium transition"
                    >
                      Xem tất cả {category.articleCount} điều →
                    </button>
                  </>
                ) : (
                  <p className="text-sm text-gray-500 text-center py-4">
                    Chưa có dữ liệu
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Popular Documents Section */}
      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          ⭐ Được Xem Nhiều
        </h2>
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="space-y-3">
            <div className="text-center text-gray-600 py-8">
              <p className="text-sm">
                Các luật phổ biến nhất sẽ hiển thị ở đây
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Help Section */}
      <div className="bg-blue-50 border border-blue-200 p-6 rounded-lg">
        <h3 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
          💡 Mẹo Sử Dụng
        </h3>
        <ul className="text-sm text-gray-700 space-y-2">
          <li>✓ Click vào bộ luật để duyệt toàn bộ điều từ bộ luật đó</li>
          <li>✓ Click vào một điều để xem chi tiết nội dung</li>
          <li>✓ Dùng thanh tìm kiếm để tìm kiếm điều luật cụ thể</li>
          <li>✓ Lưu điều luật yêu thích bằng nút 💾 để xem sau</li>
        </ul>
      </div>
    </div>
  );
}
