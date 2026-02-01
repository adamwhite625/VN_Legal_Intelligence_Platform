import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { User } from "lucide-react";

export default function SidebarUser() {
  return (
    // CHUẨN: Chiều cao 88px, Border trên, Flex giữa, Padding ngang 4
    <div className="h-[88px] border-t flex items-center px-4 bg-background shrink-0">
      <div className="flex items-center gap-3 w-full">
        <Avatar className="h-9 w-9 border shadow-sm">
          <AvatarFallback className="bg-primary text-primary-foreground">
            <User className="h-4 w-4" />
          </AvatarFallback>
        </Avatar>

        <div className="leading-tight overflow-hidden">
          <div className="text-sm font-medium truncate">Admin User</div>
          <div className="text-xs text-muted-foreground truncate">
            admin@lawyer.ai
          </div>
        </div>
      </div>
    </div>
  );
}
