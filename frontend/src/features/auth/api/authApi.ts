import axiosInstance from "@/shared/api/axiosInstance";

export async function loginApi(email: string, password: string) {
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);

  const response = await axiosInstance.post("/auth/login", formData, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });

  return response.data;
}

export async function registerApi(
  email: string,
  password: string,
  full_name: string,
) {
  const response = await axiosInstance.post("/auth/register", {
    email,
    password,
    full_name,
  });

  return response.data;
}

export async function getCurrentUser() {
  const response = await axiosInstance.get("/auth/me");
  return response.data;
}
