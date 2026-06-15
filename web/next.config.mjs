/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",            // static export → deploys to Firebase Hosting
  trailingSlash: true,         // /chat → /chat/index.html so deep links work
  images: { unoptimized: true },
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true },
};

export default nextConfig;
