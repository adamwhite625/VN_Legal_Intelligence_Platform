# Frontend Refactoring - Feature-Based Architecture

## 🎯 Cấu trúc mới (Feature-Based)

```
src/
├── app/
│   ├── router.tsx           # Tất cả routes
│   ├── providers.tsx        # App-level providers
│   └── App.tsx             # [Legacy - có thể xóa]
│
├── shared/
│   ├── ui/                 # Reusable UI components (Button, Modal, etc.)
│   ├── components/         # Shared components (Header, Footer, Layout)
│   ├── hooks/              # Custom hooks (useAuth, useLocalStorage, etc.)
│   └── utils/              # Utility functions (api.ts, constants, etc.)
│
├── features/
│   ├── auth/
│   │   ├── api/authApi.ts
│   │   ├── model/authStore.ts
│   │   ├── pages/LoginPage.tsx
│   │   ├── pages/RegisterPage.tsx
│   │   └── types.ts
│   │
│   ├── search/
│   │   ├── api/searchApi.ts
│   │   ├── components/SearchBar.tsx
│   │   ├── components/FilterPanel.tsx
│   │   ├── components/ResultCard.tsx
│   │   ├── model/searchStore.ts
│   │   ├── pages/SearchPage.tsx
│   │   └── types.ts
│   │
│   ├── law-detail/
│   │   ├── api/lawApi.ts
│   │   ├── components/LawHeader.tsx     [TODO]
│   │   ├── components/ArticleList.tsx   [TODO]
│   │   ├── components/CitationBadge.tsx [TODO]
│   │   └── pages/LawDetailPage.tsx
│   │
│   ├── consultant/
│   │   ├── api/consultantApi.ts        [TODO]
│   │   ├── components/ChatMessage.tsx   [TODO]
│   │   ├── model/consultantStore.ts
│   │   └── pages/ConsultantPage.tsx
│   │
│   └── workspace/
│       ├── components/BookmarkCard.tsx
│       ├── model/workspaceStore.ts
│       └── pages/WorkspacePage.tsx
│
├── main.tsx
└── index.css
```

## 🔑 Nguyên tắc cấu trúc

### 1. **Features** - Các tính năng độc lập

Mỗi feature chứa toàn bộ logic của nó:

- `api/` - API calls
- `model/` - State management (Zustand stores)
- `components/` - Feature-specific components
- `pages/` - Pages (routes)
- `types.ts` - TypeScript types

### 2. **Shared** - Code dùng chung

- `ui/` - Reusable UI components (Button, Input, Modal)
- `components/` - Shared components (Header, Sidebar, Layout)
- `hooks/` - Custom hooks
- `utils/` - Utilities, constants, helpers

### 3. **App** - Cấu hình ứng dụng

- `router.tsx` - Định nghĩa routes
- `providers.tsx` - Setup providers (Theme, Zustand, etc.)

## 📱 Features hiện tại

### ✅ Auth

- Login/Register pages
- Zustand store
- Persistent token management

### ✅ Search (Core)

- Search bar
- Filter panel
- Result cards
- Pagination (sẵn sàng)

### ✅ Law Detail

- Display law content
- Nested articles
- [TODO] Citations, references

### ✅ Consultant (Chat)

- Message history
- Zustand store
- [TODO] Real-time chat, API integration

### ✅ Workspace

- Bookmarks management
- [TODO] History, Statistics

## 🚀 Cách sử dụng

### Import từ features

```tsx
import { useSearchStore } from "@/features/search/model/searchStore";
import SearchPage from "@/features/search/pages/SearchPage";
```

### Import từ shared

```tsx
import { useAuth } from "@/shared/hooks/useAuth";
import { fetchWithAuth } from "@/shared/utils/api";
```

## 📝 TODO

- [ ] Tạo common UI components (Button, Input, Modal, etc.)
- [ ] Tạo Layout components (Header, Sidebar, MainLayout)
- [ ] Hoàn thiện law-detail components
- [ ] Hoàn thiện consultant API integration
- [ ] Thêm error boundary
- [ ] Thêm loading states
- [ ] Theme provider (dark/light mode)
- [ ] Admin feature (từ old App.tsx)

## 🔄 Migration từ cấu trúc cũ

Nếu bạn có code cũ, hãy:

1. Xác định feature nó thuộc vào
2. Copy file vào đúng folder
3. Update imports để dùng đúng path (`@/features/...`, `@/shared/...`)

Ví dụ:

```tsx
// ❌ Cũ
import { ChatLayout } from "../components/ChatLayout";

// ✅ Mới
import { ConsultantPage } from "@/features/consultant/pages/ConsultantPage";
```

## 📚 Tài liệu thêm

- [React Router Documentation](https://reactrouter.com/)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
